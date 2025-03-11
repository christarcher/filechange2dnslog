#!/usr/bin/env python3
import requests
import json
import hashlib
import os
import sys
import logging
from datetime import datetime

# 配置
DNSLOG_API_URL = "https://dnslog.org/token"
DNSLOG_DOMAIN = "log.dnslog.myfw.us."

NOTIFICATION_API_URL = "https://api.napcatqq.com/send_private_msg"
NOTIFICATION_API_TOKEN = "This_Is_Fake_Flag"

USER_ID = "123456789"
RECORD_FILE = "dnslog_records.json"
HASH_FILE = "dnslog_hash.txt"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dnslog_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def getDnslogRecords():
    try:
        response = requests.post(DNSLOG_API_URL, data={"domain": DNSLOG_DOMAIN})
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"获取 DNSLog 记录失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"获取 DNSLog 记录时发生错误: {str(e)}")
        return None

def sendNotification(new_records):
    # 如果你需要使用其他api,可以替换这里的逻辑
    message_text = "Dnslog记录有新的变化\n\n"
    
    for record_id, record in new_records.items():
        message_text += f"来源: {record['ip']}\n"
        message_text += f"时间: {record['time']}\n\n"
    
    payload = {
        "user_id": USER_ID,
        "message": [
            {
                "type": "text",
                "data": {
                    "text": message_text.strip()
                }
            }
        ]
    }

    headers = {
        "Authorization": NOTIFICATION_API_TOKEN,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(NOTIFICATION_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            logger.info("通知发送成功")
        else:
            logger.error(f"通知发送失败: HTTP {response.status_code}")
    except Exception as e:
        logger.error(f"发送通知时发生错误: {str(e)}")

def calcHash(records):
    records_str = json.dumps(records, sort_keys=True)
    return hashlib.sha256(records_str.encode()).hexdigest()

def loadPreviousRecords():
    """加载之前保存的记录"""
    if os.path.exists(RECORD_FILE):
        try:
            with open(RECORD_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载之前的记录时发生错误: {str(e)}")
    return {}

def loadPreviousHash():
    """加载之前保存的哈希值"""
    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"加载之前的哈希值时发生错误: {str(e)}")
    return ""

def saveRecords(records):
    """保存记录"""
    try:
        with open(RECORD_FILE, 'w') as f:
            json.dump(records, f, indent=4)
        
        hash_value = calcHash(records)
        with open(HASH_FILE, 'w') as f:
            f.write(hash_value)
            
        logger.info("记录已保存")
    except Exception as e:
        logger.error(f"保存记录时发生错误: {str(e)}")

def findNewRecords(current_records, previous_records):
    """找出新增的记录"""
    new_records = {}
    for record_id, record in current_records.items():
        if record_id not in previous_records:
            new_records[record_id] = record
    return new_records

def main():
    logger.info("开始检查 DNSLog 记录")
    current_records = getDnslogRecords()
    if current_records is None:
        logger.error("未能获取 DNSLog 记录，退出")
        return
    
    previous_records = loadPreviousRecords()
    previous_hash = loadPreviousHash()
    current_hash = calcHash(current_records)
    
    if current_hash != previous_hash:
        logger.info("检测到 DNSLog 记录有变化")
        new_records = findNewRecords(current_records, previous_records)
        
        if new_records:
            logger.info(f"发现 {len(new_records)} 条新记录")
            sendNotification(new_records)
        else:
            logger.info("记录有变化但未发现新增记录")
        
        saveRecords(current_records)
    else:
        logger.info("DNSLog 记录无变化")

if __name__ == "__main__":
    main()