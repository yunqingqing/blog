// 在这里定义接口规范
// 定义服务名称,提供server需要的注册service方法
// 封装给client调用远端service的方法
package api

import "net/rpc"

// 明确service名称
const HelloServiceName = "path/to/pkg.HelloService"

// service需实现的方法列表
type HelloServiceInterface = interface {
	Hello(request string, reply *string) error
}

// 注册服务,给远端service开发者调用
func RegisterHelloService(svc HelloServiceInterface) error {
	return rpc.RegisterName(HelloServiceName, svc)
}

// 远端服务调用客户端,给client开发者使用
type HelloServiceClient struct {
	*rpc.Client
}

var _ HelloServiceInterface = (*HelloServiceClient)(nil)

func DialHelloService(network, address string) (*HelloServiceClient, error) {
	c, err := rpc.Dial(network, address)
	if err != nil {
		return nil, err
	}
	return &HelloServiceClient{Client: c}, nil
}

// 调用远端服务封装到客户端方法中,给客户段调用,
// 现在客户端用户不用再担心RPC方法名字或参数类型不匹配等低级错误的发生。
func (p *HelloServiceClient) Hello(request string, reply *string) error {
	return p.Client.Call(HelloServiceName+".Hello", request, reply)
}
