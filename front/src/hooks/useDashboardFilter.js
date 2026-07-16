import { useCallback, useState } from "react";
import moment from "moment";

export function getDateRangeFromFlag(flag) {
  switch (flag) {
    case "yesterday":
      return {
        startDate: moment().subtract(1, "d").format("YYYY-MM-DD"),
        endDate: moment().subtract(1, "d").format("YYYY-MM-DD"),
      };
    case "last7days":
      return {
        startDate: moment().subtract(6, "d").format("YYYY-MM-DD"),
        endDate: moment().format("YYYY-MM-DD"),
      };
    case "thisMonth":
      return {
        startDate: moment().startOf("month").format("YYYY-MM-DD"),
        endDate: moment().endOf("month").format("YYYY-MM-DD"),
      };
    case "lastMonth":
      return {
        startDate: moment()
          .subtract(1, "month")
          .startOf("month")
          .format("YYYY-MM-DD"),
        endDate: moment()
          .subtract(1, "month")
          .endOf("month")
          .format("YYYY-MM-DD"),
      };
    case "today":
    default:
      return {
        startDate: moment().format("YYYY-MM-DD"),
        endDate: moment().format("YYYY-MM-DD"),
      };
  }
}

export default function useDashboardFilter(initialFlag = "today") {
  const initialRange = getDateRangeFromFlag(initialFlag);

  const [searchFlag, setSearchFlag] = useState(initialFlag);
  const [searchDate, setSearchDate] = useState({
    start: initialRange.startDate,
    end: initialRange.endDate,
  });

  const handleChangeSearchFlag = useCallback((event) => {
    const nextSearchFlag = event.target.value;
    const { startDate, endDate } = getDateRangeFromFlag(nextSearchFlag);

    setSearchFlag(nextSearchFlag);
    setSearchDate({ start: startDate, end: endDate });
  }, []);

  const handleDateChange = useCallback((event) => {
    const { name, value } = event.target;
    setSearchDate((prev) => ({ ...prev, [name]: value }));
  }, []);

  return {
    searchFlag,
    searchDate,
    handleChangeSearchFlag,
    handleDateChange,
  };
}
