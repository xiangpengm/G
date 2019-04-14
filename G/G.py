import socket
import urllib.parse

import _thread

from .utils import log

class Request():

    def __init__(self):
        self.raw_data = ''
        self.method = ''
        self.path = ''
        self.query = {}
        self.body = ''

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        log('form() 字典', f)
        return f


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
    return e.get(code, '')


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
    log('request path:', request.path)
    response = route_map.get(request.path, error)
    # 动态调用函数的例子
    return response()


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
            request = Request()
            request.raw_data = r
            header, request.body = r.split('\r\n\r\n', 1)
            h = header.split('\r\n')
            parts = h[0].split()
            request.path = parts[1]
            request.method = parts[0]
            # 用response_for_path 函数来得到path对应的响应内容
            response = response_for_request(request, route_map)
            # 把响应发送给客户端
            connection.sendall(response)
        else:
            log('接收到一个空请求')


class G(object):

    def __init__(self):
        pass

    def run(self, host, port, route_map):
        # 使用with可以保证终端的时候正确关闭socket释放占用的端口
        with socket.socket() as s:
            # 回收不用的端口
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 绑定主机和端口
            s.bind((host, port))

            # 监听接受读取请求数据解码成字符串
            s.listen()
            log('start server ip: {} port: {}'.format(host, port))

            while True:
                connection, address = s.accept()
                # 获取到请求
                # 因为chrome会发送空请求导致split得到空的list
                # 所以这里先判断一下split得到的数据的长度
                # process_connection(connection, route_map)
                _thread.start_new_thread(process_connection, (connection, route_map))