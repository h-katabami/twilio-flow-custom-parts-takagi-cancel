import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Select from "@mui/material/Select";
import { styled } from "@mui/material/styles";
import TextField from "@mui/material/TextField";

const SearchGrid = styled(Grid)(({ theme }) => ({
  marginBottom: theme.spacing(0.5),
}));

const DateInputGrid = styled(Grid)(({ theme }) => ({
  marginTop: theme.spacing(1),
  marginBottom: theme.spacing(1),
  paddingRight: theme.spacing(0.5),
}));

const SearchActionsGrid = styled(Grid)(({ theme }) => ({
  marginTop: theme.spacing(1),
  marginBottom: theme.spacing(1),
  paddingRight: theme.spacing(0.5),
}));

const LeftGroupGrid = styled(Grid)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: "8px",
  marginBottom: theme.spacing(0.5),
}));

const RightGroupGrid = styled(Grid)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: "8px",
  marginBottom: theme.spacing(0.5),
}));

export default function DashboardFilter({
  searchFlag,
  searchDate,
  maxDate,
  onChangeSearchFlag,
  onDateChange,
  onSearch,
}) {
  return (
    <Paper
      elevation={0}
      style={{ margin: "0 auto", width: "95%", background: "none" }}
    >
      <SearchGrid
        container
        style={{
          justifyContent: "space-between",
          alignItems: "center",
          gap: "8px",
        }}
      >
        <LeftGroupGrid>
          <DateInputGrid
            container
            item
            xs="auto"
            justifyContent="space-between"
            alignItems="center"
            style={{ gap: "16px", flexWrap: "nowrap" }}
          >
            <TextField
              label="開始日"
              type="date"
              name="start"
              InputLabelProps={{ shrink: true }}
              variant="standard"
              value={searchDate.start}
              onChange={onDateChange}
              inputProps={{
                max: maxDate,
              }}
            />
            〜
            <TextField
              label="終了日"
              type="date"
              name="end"
              InputLabelProps={{ shrink: true }}
              variant="standard"
              value={searchDate.end}
              onChange={onDateChange}
              inputProps={{
                min: searchDate.start,
                max: maxDate,
              }}
            />
          </DateInputGrid>
          <SearchActionsGrid item>
            <Button
              variant="contained"
              onClick={onSearch}
              style={{ margin: 4, minWidth: 88 }}
            >
              検索
            </Button>
          </SearchActionsGrid>
        </LeftGroupGrid>
        <RightGroupGrid>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <Select value={searchFlag} onChange={onChangeSearchFlag}>
              <MenuItem value="today">今日</MenuItem>
              <MenuItem value="yesterday">昨日</MenuItem>
              <MenuItem value="last7days">直近7日間</MenuItem>
              <MenuItem value="thisMonth">今月</MenuItem>
              <MenuItem value="lastMonth">先月</MenuItem>
            </Select>
          </FormControl>
        </RightGroupGrid>
      </SearchGrid>
    </Paper>
  );
}
