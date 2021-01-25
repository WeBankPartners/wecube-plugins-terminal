<?xml version="1.0" encoding="UTF-8"?>
<package name="terminal" version="{{PLUGIN_VERSION}}">
    <!-- 1.依赖分析 - 描述运行本插件包需要的其他插件包 -->
    <packageDependencies>
        <packageDependency name="platform" version="v2.5.0" />
        <packageDependency name="itsdangerous" version="v0.1.0" />
    </packageDependencies>

    <!-- 2.菜单注入 - 描述运行本插件包需要注入的菜单 -->
    <menus>
        <menu code='IMPLEMENTATION_TERMINAL' cat='IMPLEMENTATION' displayName="terminal" localDisplayName="远程终端">/terminalIndex</menu>
    </menus>

    <!-- 3.数据模型 - 描述本插件包的数据模型,并且描述和Framework数据模型的关系 -->
    <dataModel></dataModel>

    <!-- 4.系统参数 - 描述运行本插件包需要的系统参数 -->
    <systemParameters>
        <systemParameter name="TERMINAL_ASSET_TYPE" scopeType="plugins" defaultValue="wecmdb:host_resource_instance"/>
        <systemParameter name="TERMINAL_FIELD_NAME" scopeType="plugins" defaultValue="name"/>
        <systemParameter name="TERMINAL_FIELD_IP" scopeType="plugins" defaultValue="ip_address"/>
        <systemParameter name="TERMINAL_FIELD_PORT" scopeType="plugins" defaultValue="login_port"/>
        <systemParameter name="TERMINAL_FIELD_USER" scopeType="plugins" defaultValue="user_name"/>
        <systemParameter name="TERMINAL_FIELD_PASSWORD" scopeType="plugins" defaultValue="user_password"/>
        <systemParameter name="TERMINAL_FIELD_DESC" scopeType="plugins" defaultValue="description"/>
        <systemParameter name="TERMINAL_BOXES" scopeType="plugins" defaultValue="all"/>
    </systemParameters>

    <!-- 5.权限设定 -->
    <authorities>
        <authority systemRoleName="SUPER_ADMIN" >
            <menu code="IMPLEMENTATION_TERMINAL" />
        </authority >
    </authorities>

    <!-- 6.运行资源 - 描述部署运行本插件包需要的基础资源(如主机、虚拟机、容器、数据库等) -->
    <resourceDependencies>
        <docker imageName="{{IMAGENAME}}" containerName="{{CONTAINERNAME}}" 
        portBindings="{{ALLOCATE_PORT}}:9001,19002:9002"
        volumeBindings="/etc/localtime:/etc/localtime,{{BASE_MOUNT_PATH}}/terminal/logs:/var/log/terminal,{{BASE_MOUNT_PATH}}/certs:/certs,{{BASE_MOUNT_PATH}}/terminal/records:/data/terminal/records" 
        envVariables="TERMINAL_DB_USERNAME={{DB_USER}},TERMINAL_DB_PASSWORD={{DB_PWD}},TERMINAL_DB_HOSTIP={{DB_HOST}},TERMINAL_DB_HOSTPORT={{DB_PORT}},TERMINAL_DB_SCHEMA={{DB_SCHEMA}},TERMINAL_ASSET_TYPE={{TERMINAL_ASSET_TYPE}},TERMINAL_FIELD_NAME={{TERMINAL_FIELD_NAME}},TERMINAL_FIELD_IP={{TERMINAL_FIELD_IP}},TERMINAL_FIELD_PORT={{TERMINAL_FIELD_PORT}},TERMINAL_FIELD_USER={{TERMINAL_FIELD_USER}},TERMINAL_FIELD_PASSWORD={{TERMINAL_FIELD_PASSWORD}},TERMINAL_FIELD_DESC={{TERMINAL_FIELD_DESC}},GATEWAY_URL={{GATEWAY_URL}},JWT_SIGNING_KEY={{JWT_SIGNING_KEY}},TERMINAL_BOXES={{TERMINAL_BOXES}},SUB_SYSTEM_CODE={{SUB_SYSTEM_CODE}},SUB_SYSTEM_KEY={{SUB_SYSTEM_KEY}}" />
        <mysql schema="terminal" initFileName="init.sql" upgradeFileName="upgrade.sql" />
    </resourceDependencies>

    <!-- 7.插件列表 - 描述插件包中单个插件的输入和输出 -->
    <plugins></plugins>
</package>
