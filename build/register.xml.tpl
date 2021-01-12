<?xml version="1.0" encoding="UTF-8"?>
<package name="terminal" version="{{PLUGIN_VERSION}}">
    <!-- 1.依赖分析 - 描述运行本插件包需要的其他插件包 -->
    <packageDependencies>
        <packageDependency name="platform" version="v2.5.0" />
    </packageDependencies>

    <!-- 2.菜单注入 - 描述运行本插件包需要注入的菜单 -->
    <menus>
        <menu code='ADMIN_TERMINAL' cat='ADMIN' displayName="terminal" localDisplayName="远程终端">/terminalIndex</menu>
    </menus>

    <!-- 3.数据模型 - 描述本插件包的数据模型,并且描述和Framework数据模型的关系 -->
    <dataModel></dataModel>

    <!-- 4.系统参数 - 描述运行本插件包需要的系统参数 -->
    <systemParameters></systemParameters>

    <!-- 5.权限设定 -->
    <authorities>
        <authority systemRoleName="SUPER_ADMIN" >
            <menu code="ADMIN_TERMINAL" />
        </authority >
    </authorities>

    <!-- 6.运行资源 - 描述部署运行本插件包需要的基础资源(如主机、虚拟机、容器、数据库等) -->
    <resourceDependencies>
        <docker imageName="{{IMAGENAME}}" containerName="{{CONTAINERNAME}}" 
        portBindings="{{ALLOCATE_PORT}}:9000" 
        volumeBindings="/etc/localtime:/etc/localtime,{{BASE_MOUNT_PATH}}/terminal/logs:/var/log/terminal,{{BASE_MOUNT_PATH}}/certs:/certs" 
        envVariables="TERMINAL_DB_USERNAME={{DB_USER}},TERMINAL_DB_PASSWORD={{DB_PWD}},
        TERMINAL_DB_HOSTIP={{DB_HOST}},TERMINAL_DB_HOSTPORT={{DB_PORT}},TERMINAL_DB_SCHEMA={{DB_SCHEMA}},
        GATEWAY_URL={{GATEWAY_URL}},JWT_SIGNING_KEY={{JWT_SIGNING_KEY}}" />
        <mysql schema="terminal" initFileName="init.sql" upgradeFileName="upgrade.sql" />
    </resourceDependencies>

    <!-- 7.插件列表 - 描述插件包中单个插件的输入和输出 -->
    <plugins></plugins>
</package>
