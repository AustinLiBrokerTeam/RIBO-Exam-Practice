import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class RangeRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        self._range_to_send = None
        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()

        path = self.translate_path(self.path)
        if os.path.isdir(path) or not os.path.isfile(path):
            return super().send_head()

        match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
        file = open(path, "rb")
        file_size = os.fstat(file.fileno()).st_size
        if not match or not any(match.groups()):
            file.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        first, last = match.groups()
        if first:
            start = int(first)
            end = int(last) if last else file_size - 1
        else:
            suffix_length = int(last)
            start = max(file_size - suffix_length, 0)
            end = file_size - 1

        if start >= file_size or end < start:
            file.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        end = min(end, file_size - 1)
        content_length = end - start + 1
        self._range_to_send = (start, content_length)

        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(content_length))
        self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(path)))
        self.end_headers()
        return file

    def copyfile(self, source, output_file):
        byte_range = getattr(self, "_range_to_send", None)
        if byte_range is None:
            return super().copyfile(source, output_file)

        start, remaining = byte_range
        source.seek(start)
        while remaining:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            output_file.write(chunk)
            remaining -= len(chunk)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), RangeRequestHandler)
    print(f"RIBO Practice Portal running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
