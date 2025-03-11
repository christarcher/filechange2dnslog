# FileChange2Dnslog

用于监测受控机器上的指定文件的变化,并通过Dnslog来传递信息

尤其适合**不出网**或者**白名单**的环境
适合监控配置文件,脚本,ELF等

当指定文件发生变化后,会nslookup指定的Dnslog域名,服务端定期监测变化,监测到有信记录就调用api发送通知



## 使用
首先需要修改配置,客户端需要修改dnslog.org域名
服务端要修改dnslog.org的域名,token和你的onebot api配置

默认使用Onebot QQ API来提醒,你也可以替换为你自己的api,比如tg机器人等

服务端和客户端都使用crontab来定期运行,这样也防止留存一个进程而被发现,更加健壮
```bash
crontab -e

*/2 * * * * /usr/bin/python3 /path/to/dnslog_monitor.py # 服务端
*/1 * * * * bash /root/dnslog_check_hash.sh # 客户端
```
