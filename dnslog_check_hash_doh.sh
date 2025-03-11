#!/bin/bash

# 参数
# 需要的系统指令有: [nslookup, md5sum] (基本都是自带的,但是最好检查一下)
FILE_TO_MONITOR="esxi.flow" # 填你自己要监测变化的文件
HASH_STORAGE="esxi_hash.md5" # 填一个能存放文件哈希的位置
DOMAIN_TO_PING="xxxxxxxx.log.dnslog.myfw.us" # 填dnslog域名

if [ ! -f "$FILE_TO_MONITOR" ]; then
    exit 1
fi

CURRENT_HASH=$(md5sum "$FILE_TO_MONITOR" | awk '{print $1}')

if [ -f "$HASH_STORAGE" ]; then
    PREVIOUS_HASH=$(cat "$HASH_STORAGE")
    if [ "$CURRENT_HASH" != "$PREVIOUS_HASH" ]; then
        curl "https://223.5.5.5/resolve?name=$DOMAIN_TO_PING&type=A" -k -o /dev/null
        curl -H "Accept: application/dns-json" "https://1.1.1.1/dns-query?name=$DOMAIN_TO_PING&type=A" -k -o /dev/null
        echo "$CURRENT_HASH" > "$HASH_STORAGE"
    fi
else
    echo "$CURRENT_HASH" > "$HASH_STORAGE"
fi