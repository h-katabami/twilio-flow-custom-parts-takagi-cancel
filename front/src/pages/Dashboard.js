import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import { styled } from "@mui/material/styles";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useState } from "react";

import DashboardFilter from "../components/DashboardFilter";
import GraphDashboard from "../components/GraphDashboard";
import { useAuth } from "../hooks/use-auth";
import useDashboardFilter, {
  getDateRangeFromFlag,
} from "../hooks/useDashboardFilter";

import moment from "moment";

import useApi from "../hooks/useApi"; // カスタムフック

const CustomContainer = styled(Container)(({ theme }) => ({
  height: "92vh",
  padding: theme.spacing(5),
  paddingTop: theme.spacing(2),
}));

function toCountDict(array, column, isDateRange, status) {
  let dict = [];
  for (let key of column) {
    dict.push(
      array.filter((x) => {
        var dictKey = isDateRange
          ? moment(x.start_time).format("YYYY-MM-DD")
          : new Date(x.start_time).getHours();
        if (status === null) {
          return dictKey === key;
        } else {
          return dictKey === key && x.status === status;
        }
      }).length
    );
  }
  return dict;
}
function toCountDictSum(array) {
  return array.reduce((sum, element) => sum + element, 0);
}

const defaultStatusList = [
  "冒頭切断",
  "ビジー切断",
  "切断(お客様ナンバー)",
  "切断(電話番号1)",
  "切断(電話番号2)",
  "切断(郵便番号1)",
  "切断(郵便番号2)",
  "切断(名前1)",
  "切断(名前2)",
  "特定NG時間内",
  "特定NG時間外",
  "受付NG時間内",
  "受付NG時間外",
  "切断(交換変更日)",
  "希望日確認NG時間内",
  "希望日確認NG時間外",
  "音声認識エラー時間内",
  "音声認識エラー時間外",
  "対応完了",
  "SMS案内",
  "SMS送信",
];

export default function Dashboard() {
  const { user } = useAuth();
  const [token, setToken] = useState(null);
  // const token = auth.idToken;
  const [data, setData] = useState([]);
  const [statusList, setStatusList] = useState(defaultStatusList);
  const [list, setList] = useState({});
  const [total, setTotal] = useState({});
  const {
    searchFlag,
    searchDate,
    handleChangeSearchFlag,
    handleDateChange,
  } = useDashboardFilter("today");
  const [column, setColumn] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [customStatusListState, setCustomStatusListState] = useState([]);
  const api = useApi();

  const handleClickSearch = () => {
    if (token) {
      getCallList(searchDate.start, searchDate.end, token);
    }
  };
  // const statusList = customStatusList.concat(defaultStatusList);

  const countColumn = useCallback((array, startDate, endDate, statusList) => {
    const isDateRange = startDate !== endDate;
    let columnValues = [];

    if (!isDateRange) {
      columnValues = [...Array(24).keys()];
    } else {
      for (let date = moment(startDate); date <= moment(endDate); date.add(1, "d")) {
        columnValues.push(date.format("YYYY-MM-DD"));
      }
    }

    const statusCounts = {};
    statusList.forEach((value) => {
      statusCounts[value] = toCountDict(array, columnValues, isDateRange, value);
    });
    statusCounts["all"] = toCountDict(array, columnValues, isDateRange, null);

    return { column: columnValues, list: statusCounts };
  }, []); // 依存配列は空

  // ステータスごとの合計値を算出
  const countStatusTotal = useCallback((list, statusList) => {
    const statusTotal = {};
    statusList.forEach((value) => {
      statusTotal[value] = toCountDictSum(list[value]);
    });
    return statusTotal;
  }, []); // 依存配列は空

  const getCallList = useCallback(
    async (startDate, endDate, currentToken) => {
      setLoading(true);
      setError(null);
      if (!currentToken) {
        setLoading(false);
        setError("トークンがありません");
        return;
      }

      const start = moment(startDate).format("YYYY-MM-DD");
      const end = moment(endDate).add(1, "d").format("YYYY-MM-DD");

      try {
        const response = await api.get("/edit/histories", {
          params: {
            start: start,
            end: end,
          },
        });

        const descData = response.results;
        descData.sort(
          (a, b) => new Date(b.start_time) - new Date(a.start_time)
        );
        const customStatus = [...new Set(descData.map((v) => v.status))];
        setCustomStatusListState(customStatus);

        const uniqueCustomStatus = customStatus.filter(
          (status) => !defaultStatusList.includes(status)
        );
        const sortedStatusList = [...defaultStatusList, ...uniqueCustomStatus];
        setStatusList(sortedStatusList);

        // `countColumn` にも修正後のソート済みリストを渡す
        const { column: newColumn, list: newList } = countColumn(
          descData,
          startDate,
          endDate,
          sortedStatusList
        );

        const newTotal = countStatusTotal(newList, sortedStatusList);
        setData(descData);
        setColumn(newColumn);
        setList(newList);
        setTotal(newTotal);
      } catch (err) {
        console.error(err);
        setError("データの取得に失敗しました");
        setList({});
        setTotal({});
      } finally {
        setLoading(false);
      }
    },
    [countColumn, countStatusTotal, api]
  );

  // トークンを取得する useEffect
  useEffect(() => {
    if (user && user.signInUserSession && user.signInUserSession.idToken) {
      setToken(user.signInUserSession.idToken.jwtToken);
    } else {
      setToken(null);
      console.warn("IDトークンが見つかりませんでした。");
    }
  }, [user]);

  // searchFlag または token が変更された場合にデータ取得を行う useEffect
  useEffect(() => {
    if (token) {
      const { startDate, endDate } = getDateRangeFromFlag(searchFlag);
      getCallList(startDate, endDate, token);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchFlag, token]);

  if (loading) {
    return <div>Loading...</div>; // ローディング表示
  }

  if (error) {
    return <div>Error: {error}</div>; // エラー表示
  }

  return (
    <CustomContainer>
      <DashboardFilter
        searchFlag={searchFlag}
        searchDate={searchDate}
        maxDate={moment().format("YYYY-MM-DD")}
        onChangeSearchFlag={handleChangeSearchFlag}
        onDateChange={handleDateChange}
        onSearch={handleClickSearch}
      />
      <GraphDashboard
        labels={
          searchDate.start === searchDate.end
            ? column.map((v) => v + ":00")
            : column
        }
        datalist={list}
        statusList={statusList}
      />
      <Paper
        elevation={0}
        style={{
          margin: "0 auto",
          width: "95%",
          background: "none",
          marginTop: "1rem",
        }}
      >
        <Grid
          container
          justify="space-around"
          style={{ marginBottom: "0.5rem", justifyContent: "space-between" }}
        >
          <Grid item xs={2}>
            <Card
              variant="outlined"
              // sx={{ minWidth: 195 }}
              style={{ margin: "0 5px 0 0" }}
            >
              <CardContent style={{ textAlign: "center" }}>
                <Typography
                  sx={{ fontSize: 14 }}
                  color="text.secondary"
                  gutterBottom
                >
                  着信数
                </Typography>
                <Typography variant="h5" component="div" textAlign="center">
                  {data.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={10}>
            <Card
              variant="outlined"
              style={{
                margin: "0 0px 0 5px",
                display: "flex",
                justifyContent: "space-around",
              }}
            >
              {Object.keys(total)
                .filter((v) => !defaultStatusList.includes(v))
                .map((key, index) => {
                  return (
                    <div key={index}>
                      <CardContent
                        sx={{ minWidth: 135 }}
                        style={{ textAlign: "center" }}
                      >
                        <Typography
                          sx={{ fontSize: 14 }}
                          color="text.secondary"
                          gutterBottom
                        >
                          {key}
                        </Typography>
                        <Typography variant="h5" component="div">
                          {total[key]}
                        </Typography>
                      </CardContent>
                    </div>
                  );
                })}
            </Card>
            <Card
              variant="outlined"
              sx={{ minWidth: 185 }}
              style={{ margin: "0 0px 0 5px", display: "flex" }}
            >
              <Grid container>
                {defaultStatusList.map((key, index) => {
                  return (
                    <div key={index}>
                      <Grid item xs={2} sm={4} md={4} key={index}>
                        <CardContent
                          sx={{ width: 182 }}
                          style={{ textAlign: "center" }}
                        >
                          <div style={{ height: "48px" }}>
                            <Typography
                              sx={{ fontSize: 13.7 }}
                              color="text.secondary"
                              gutterBottom
                            >
                              {key}
                            </Typography>
                          </div>
                          <Typography variant="h5" component="div">
                            {total[key]}
                          </Typography>
                        </CardContent>
                      </Grid>
                    </div>
                  );
                })}
              </Grid>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </CustomContainer>
  );
}
