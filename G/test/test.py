from G import G
from G import html_content


g = G()


def route_index():
    """
    主页的处理函数, 返回主页的响应
    :return:
    :rtype:
    """
    header = 'HTTP/1.1 233 very OK\r\nContent-Type: text/html\r\n'
    body = '<h1>Hello World</h1><img src="doge.gif"/>'
    r = '{}\r\n{}'.format(header, body)
    return r.encode()


def route_message():
    """
    主页的处理函数, 返回主页的响应
    """
    header = 'HTTP/1.1 233 OK\r\nContent-Type: text/html\r\n'
    body = html_content('templates/html_basic.html')
    r = '{}\r\n{}'.format(header, body)
    return r.encode()


def route_image():
    """
    图片的处理函数, 读取图片并生成响应返回
    """
    with open('static/doge.gif', 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n\r\n'
        image = header + f.read()
        return image


def route_dict():
    route_map = {
        '/': route_index,
        '/message': route_message,
        '/doge.gif': route_image,
    }
    return route_map

if __name__ == "__main__":
    # 这里面只能传路由映射还没有实现传参的功能
    route_map = route_dict()
    # 配置服务器
    config = dict(
        host='0.0.0.0',
        port=3000,
        route_map=route_map
    )
    # 运行服务器
    g.run(**config)