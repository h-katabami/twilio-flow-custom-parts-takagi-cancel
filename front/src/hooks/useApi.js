import axios from "axios";
import { useCallback, useState } from "react";
import { useAuth } from "../hooks/use-auth";

const useApi = () => {
  const defaultBaseUrl = process.env.REACT_APP_API_BASE_URL; 
  const auth = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const api = useCallback(
    async (method, url, data = {}, config = {}) => {
      setLoading(true);
      setError(null);

      try {
        const token = auth?.user?.signInUserSession?.idToken?.jwtToken;

        // 1. URLの決定
        // url自体が http から始まる完全なURLならそのまま使い、そうでなければ baseUrl と結合する
        const isFullUrl = url.startsWith("http");
        const activeBaseUrl =
          config.baseUrl !== undefined ? config.baseUrl : defaultBaseUrl;
        const requestUrl = isFullUrl ? url : `${activeBaseUrl}${url}`;

        // 2. ヘッダーの構築
        const headers = { ...config?.headers };
        if (!config.skipAuth && token) {
          headers.Authorization = `Bearer ${token}`;
        }

        const response = await axios({
          method: method.toLowerCase(),
          url: requestUrl,
          data: data,
          headers: headers,
          ...config,
        });

        return response.data;
      } catch (err) {
        console.error("API Error:", err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [auth, defaultBaseUrl]
  );

  // 各メソッドの定義
  const get = useCallback((url, config = {}) => api("get", url, {}, config), [
    api,
  ]);
  const post = useCallback(
    (url, data, config = {}) => api("post", url, data, config),
    [api]
  );
  const put = useCallback(
    (url, data, config = {}) => api("put", url, data, config),
    [api]
  );
  const del = useCallback(
    (url, config = {}) => api("delete", url, {}, config),
    [api]
  );

  return { get, post, put, delete: del, loading, error };
};

export default useApi;
