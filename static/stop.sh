#!/bin/sh
#定义程序名 项目名称
PROJECT_NAME='top'
## 编写判断程序是否正在运行的方法
isExist(){
	## 首先查找进程号
    pid=`ps -ef | grep ${PROJECT_NAME} | grep -v grep | awk '{print $2}'`
    ## 如果进程号不存在，则返回0 否则返回1
    if [ -z "${pid}" ]; then
    	return 0
    else
    	return 1
    fi
}

## 编写停止程序的方法
stop(){
    ## 调用 判断程序是否正在运行
    isExist
    ## 判断是否存在，返回值0不存在
    if [ $? -eq "0" ]; then
    	echo "${PROJECT_NAME} is not running ......"
    else
    	echo "${PROJECT_NAME} is running, pid=${pid}, prepare kill it "
    	kill -9 ${pid}
    	echo "${PROJECT_NAME} has been successfully killed ......"
    fi
}

stop

## 程序最开始执行的
## 根据用户输入，判断执行方法
##case "$1" in
##	"stop")
##		stop
##		;;
##	*)
##		echo "please enter the correct commands: "
##		echo "such as : sh stop.sh [  stop  ]"
##		;;
##esac

