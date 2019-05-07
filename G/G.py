import os
import socket
import urllib.parse
import _thread

from .utils import log
from jinja2 import Environment, FileSystemLoader


class Request():

    def __init__(self, r):
        self.raw_data = r
        header, self.body = r.split('\r\n\r\n', 1)
        h = header.split('\r\n')
        parts = h[0].split()
        log(parts)
        self.path = parts[1]
        log('path', self.path)
        self.method = parts[0]
        self.path, self.query = self.parsed_path(self.path)
        self.headers = {}
        self.cookies = {}

    def add_headers(self, header):
        """
        Cookie: user=gua
        """
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            k, v = cookies.split('=')
            self.cookies[k] = v

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        # log('form', self.body)
        # log('form', body)
        args = body.split('&')
        f = {}
        # log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        # log('form() 字典', f)
        return f

    def parsed_path(self, path):
        index = path.find('?')
        if index == -1:
            return path, {}
        else:
            query_string = path[index + 1:]
            p = path[:index]
            args = query_string.split('&')
            query = {}
            for arg in args:
                k, v = arg.split('=')
                query[k] = v
            return p, query


def html_content(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def error(code=404):
    """
    根据code返回不同的错误响应
    目前只有404
    :return:
    :rtype:
    """
    e = {
        404: b'HTTP/1.1 404 NOT FOUND\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>'
    }
    return e.get(code, b'')


def response_for_request(request, route_map):
    """
    根据path调用响应的处理函数
    没有处理的path会返回404
    :param path:
    :type path:
    :return:
    :rtype:
    """
    # 表驱动法
    # 高阶函数: 函数也是一个对象, 函数可以被当成参数传递
    # r = {
    #     '/': route_index,
    #     '/message': route_message,
    #     '/doge.gif': route_image,
    #
    # 处理path query
    # log('request path:', request.path)
    # request.path, request.query = parsed_path(request.path)
    log('request query', request.query)
    response = route_map.get(request.path, error)
    # 动态调用函数的例子
    log('route func name: ', response.__name__)

    # 在这里执行回调函数
    return response(request)


def request_from_connection(connection):
    request = b''
    buffer_size = 1024
    while True:
        r = connection.recv(buffer_size)
        request += r
        if len(r) < buffer_size:
            request = request.decode()
            return request


def process_connection(connection, route_map):
    with connection:
        r = request_from_connection(connection)
        if len(r) > 0:
            request = Request(r)
            # 用response_for_path 函数来得到path对应的响应内容
            response = response_for_request(request, route_map)
            # 把响应发送给客户端
            connection.sendall(response)
        else:
            log('接收到一个空请求')


def response_with_headers(headers, code=200):
    """
    Content-Type: text/html
    Set-Cookie: user=gua
    """
    header = 'HTTP/1.x {} VERY OK\r\n'.format(code)
    header += ''.join([
        '{}: {}\r\n'.format(k, v) for k, v in headers.items()
    ])
    return header


def redirect(url):
    """
    浏览器在收到 302 响应的时候
    会自动在 HTTP header 里面找 Location 字段并获取一个 url
    然后自动请求新的 url
    """
    headers = {
        'Location': url,
    }
    # 增加 Location 字段并生成 HTTP 响应返回
    # 注意, 没有 HTTP body 部分
    r = response_with_headers(headers, 302) + '\r\n'
    return r.encode()


class G(object):

    def __init__(self, file_path):
        path = os.path.join(os.path.dirname(file_path), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(path))
        self.route_map = {}

    def run(self, host, port):
        # 使用with可以保证终端的时候正确关闭socket释放占用的端口
        with socket.socket() as s:
            # 回收不用的端口
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 绑定主机和端口
            s.bind((host, port))

            # 监听接受读取请求数据解码成字符串
            s.listen()
            log('start server ip: http://{}:{}'.format(host, port))

            while True:
                connection, address = s.accept()
                # 获取到请求 
                # 因为chrome会发送空请求导致split得到空的list
                # 所以这里先判断一下split得到的数据的长度
                # process_connection(connection, route_map)
                _thread.start_new_thread(process_connection, (connection, self.route_map))

    def route(self, path):
        def wrap(func):
            self.route_map[path] = func
        return wrap


    def render_templates(self, name, **kwargs):
        temp = self.jinja_env.get_template(name)
        return temp.render(**kwargs)


    def render_string(self, template, **kwargs):
        temp = self.jinja_env.from_string(template)
        return temp.render(**kwargs)