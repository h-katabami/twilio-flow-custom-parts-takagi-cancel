import { styled } from "@mui/material/styles";
import { useState } from "react";

import DownloadIcon from "@mui/icons-material/Download";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import LinearProgress from "@mui/material/LinearProgress";
import TextField from "@mui/material/TextField";

import axios from "axios";
import moment from "moment";

// import StickyHeadTable from "../components/StickyHeadTable";
// import { useAuth } from "../hooks/use-auth";
import useApi from "../hooks/useApi"; // カスタムフック

import { Typography } from "@mui/material";

const CustomContainer = styled(Container)(({ theme }) => ({
  padding: theme.spacing(5),
  paddingTop: theme.spacing(2),
}));

export default function FileDownload() {
  const { post } = useApi();
  // const auth = useAuth();
  // const token = auth.idToken;

  const today = moment();
  const [searchDate, setSearchDate] = useState({
    start: today.startOf("day").format("YYYY-MM-DDTHH:mm"),
    end: today.endOf("day").format("YYYY-MM-DDTHH:mm"),
  });
  const [rows, setRows] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleChangeDate = (e) => {
    const value = e.target.value;
    const name = e.target.name;
    switch (name) {
      case "searchDateStart":
        setSearchDate({
          ...searchDate,
          start: value,
          end: moment(value).isAfter(moment(searchDate.end))
            ? value
            : searchDate.end,
        });
        break;
      case "searchDateEnd":
        setSearchDate({ ...searchDate, end: value });
        break;
      default:
        break;
    }
  };
  const handleSubmit = async () => {
    setIsLoading(true);
    setMessage("");

    const downloadApiBase = process.env.REACT_APP_PROXY_BASE_URL;

    try {
      // 1) まず、自社APIから「ダウンロード用URL」を取得する
      // この時点では通常のJSONレスポンスを受け取ります
      const response = await post(
        "/services/TakagiCancel/customer-data/download",
        {
          dateFrom: `${searchDate.start}:00`,
          dateTo: `${searchDate.end}:59`,
        },
        { baseUrl: downloadApiBase }
      );

      // レスポンスから downloadUrl を抽出
      const { downloadUrl } = response;

      if (!downloadUrl) {
        throw new Error("ダウンロードURLの取得に失敗しました。");
      }

      // 2) useApi を通さず、axios を直接使って S3 から取得
      // ここでは axios.create() を使うか、直接 axios() を呼びます。
      // ポイント：一切の共通ヘッダー（Authorizationなど）を乗せないようにします。
      const fileRes = await axios({
        method: "GET",
        url: downloadUrl,
        // responseType: "blob" は必須です
        responseType: "blob",
        // transformRequest などを空にして、共通設定の影響を完全に排除します
        transformRequest: [
          (data, headers) => {
            // 共通設定で Authorization が入ってしまうのを防ぐため、明示的に削除
            if (headers.common) {
              delete headers.common["Authorization"];
              delete headers.common["bearer"]; // 小文字の場合も考慮
            }
            // リクエスト直接ヘッダーにセットされている場合も削除
            delete headers["Authorization"];
            delete headers["bearer"];
            return data;
          },
        ],
      });

      // --- ブラウザでの保存処理 ---
      const url = window.URL.createObjectURL(new Blob([fileRes.data]));
      const link = document.createElement("a");
      link.href = url;

      const fileName = `aic_${moment().format("YYYYMMDD_HHmmss")}.csv`;
      link.setAttribute("download", fileName);

      document.body.appendChild(link);
      link.click();

      // 後片付け
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);

      setRows([1]);
      setMessage("ダウンロードが完了しました！");
    } catch (err) {
      console.error("Download Error Detail:", err);
      setMessage(
        "ダウンロードに失敗しました。URLの有効期限切れか、通信エラーの可能性があります。"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <CustomContainer>
      <Grid container justify="space-around" style={{ marginBottom: "0.5rem" }}>
        <TextField
          id="datetime-start"
          label="検索開始日時"
          type="datetime-local"
          name={"searchDateStart"}
          InputLabelProps={{
            shrink: true,
          }}
          variant="standard"
          value={searchDate.start}
          onChange={(event) => handleChangeDate(event)}
        />
        〜
        <TextField
          id="datetime-end"
          label="検索終了日時"
          type="datetime-local"
          inputProps={{
            min: searchDate.start,
            max: moment().format("YYYY-MM-DDTHH:mm"),
          }}
          name={"searchDateEnd"}
          InputLabelProps={{
            shrink: true,
          }}
          variant="standard"
          value={searchDate.end}
          onChange={(event) => handleChangeDate(event)}
        />
        <Button
          variant="contained"
          size="small"
          color="secondary"
          startIcon={<DownloadIcon />}
          style={{ margin: "5px 10px" }}
          onClick={() => handleSubmit()}
          disabled={isLoading}
        >
          ダウンロード
        </Button>
      </Grid>
      {rows.length > 0 && !isLoading ? (
        <Typography>{message}</Typography>
      ) : isLoading ? (
        <LinearProgress />
      ) : (
        <Typography>日時を選択し、データをダウンロードしてください</Typography>
      )}
      {/* <Typography>ダウンロード条件</Typography> */}
    </CustomContainer>
  );
}
