import unittest
import log_analyzer
import time


class TestSuite(unittest.TestCase):
    def setUp(self):
        pass

    def test_log_info_parsing(self):
        test_row = ['1.126.153.80', '-', '-', '[29/Jun/2017:04:06:36 +0300]', 'GET /api/v2/banner/23964943 HTTP/1.1',
                    '200', '939', '-', '-', '-', '1498698395-48424485-4709-9935542', '1835ae0f17f', '0.609']
        log_info = log_analyzer.parse_log_info(iter(test_row))
        self.assertEqual(log_info.remote_addr, '1.126.153.80')
        self.assertEqual(log_info.remote_user, '-')
        self.assertEqual(log_info.http_x_real_ip, '-')
        self.assertEqual(log_info.time_local, time.strptime("29/Jun/2017:04:06:36 +0300", "%d/%b/%Y:%H:%M:%S %z"))
        self.assertEqual(log_info.request, 'GET /api/v2/banner/23964943 HTTP/1.1')
        self.assertEqual(log_info.status, '200')
        self.assertEqual(log_info.body_bytes_sent, '939')
        self.assertEqual(log_info.http_referer, '-')
        self.assertEqual(log_info.http_user_agent, '-')
        self.assertEqual(log_info.http_x_forwarded_for, '-')
        self.assertEqual(log_info.http_X_REQUEST_ID, '1498698395-48424485-4709-9935542')
        self.assertEqual(log_info.http_X_RB_USER, '1835ae0f17f')
        self.assertEqual(log_info.request_time, 0.609)
        self.assertEqual(log_info.request_clear(), "/api/v2/banner/23964943")

    def test_stat_info_trivial(self):
        stat_info = log_analyzer.StatInfo("test")
        stat_info.append_time(1.0)
        stat_info.append_time(1.0)
        stat_info.append_time(1.0)
        stat_info.append_time(1.0)
        self.assertEqual(stat_info.count(), 4)
        self.assertEqual(stat_info.request_times_sum(), 4.0)
        self.assertEqual(stat_info.request_times_max(), 1.0)
        self.assertEqual(stat_info.request_times_avg(), 1.0)
        self.assertEqual(stat_info.request_times_median(), 1.0)

    def test_stat_info_ordered(self):
        stat_info = log_analyzer.StatInfo("test")
        stat_info.append_time(1.0)
        stat_info.append_time(2.0)
        stat_info.append_time(3.0)
        stat_info.append_time(4.0)
        self.assertEqual(stat_info.count(), 4)
        self.assertEqual(stat_info.request_times_sum(), 10.0)
        self.assertEqual(stat_info.request_times_max(), 4.0)
        self.assertEqual(stat_info.request_times_avg(), 2.5)
        self.assertEqual(stat_info.request_times_median(), 2.5)


    def test_stat_info(self):
        stat_info = log_analyzer.StatInfo("test")
        stat_info.append_time(10.0)
        stat_info.append_time(12.0)
        stat_info.append_time(3.0)
        stat_info.append_time(5.0)
        stat_info.append_time(6.0)
        stat_info.append_time(0.25)
        self.assertEqual(stat_info.count(), 6)
        self.assertEqual(stat_info.request_times_sum(), 36.25)
        self.assertEqual(stat_info.request_times_max(), 12.0)
        self.assertEqual(stat_info.request_times_avg(), 6.041666666666667)
        self.assertEqual(stat_info.request_times_median(), 5.5)


if __name__ == "__main__":
    unittest.main()
