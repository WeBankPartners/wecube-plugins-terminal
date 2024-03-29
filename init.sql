SET FOREIGN_KEY_CHECKS = 0;

--
-- Table structure for table `permission`
--

CREATE TABLE `permission` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `enabled` tinyint(4) NOT NULL,
  `auth_upload` tinyint(4) NOT NULL,
  `auth_download` tinyint(4) NOT NULL,
  `auth_execute` tinyint(4) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `permission_asset`
--

CREATE TABLE `permission_asset` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `permission_id` bigint(20) unsigned NOT NULL,
  `asset_id` varchar(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `permission_asset_FK` (`permission_id`),
  CONSTRAINT `permission_asset_FK` FOREIGN KEY (`permission_id`) REFERENCES `permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `permission_role`
--

CREATE TABLE `permission_role` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `permission_id` bigint(20) unsigned NOT NULL,
  `role` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `permission_role_FK` (`permission_id`),
  CONSTRAINT `permission_role_FK` FOREIGN KEY (`permission_id`) REFERENCES `permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `session_record`
--

CREATE TABLE `session_record` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `asset_id` varchar(36) NOT NULL,
  `filepath` varchar(255) NOT NULL,
  `user` varchar(36) NOT NULL,
  `started_time` datetime NOT NULL,
  `ended_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `transfer_record`
--

CREATE TABLE `transfer_record` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `asset_id` varchar(36) NOT NULL,
  `filepath` varchar(255) NOT NULL,
  `filesize` bigint(20) unsigned NOT NULL,
  `user` varchar(36) NOT NULL,
  `operation_type` varchar(36) NOT NULL,
  `started_time` datetime NOT NULL,
  `ended_time` datetime DEFAULT NULL,
  `status` varchar(36) DEFAULT NULL,
  `message` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;

#@v0.1.0.1-begin@;
ALTER TABLE `session_record` ADD filesize BIGINT UNSIGNED NULL;
ALTER TABLE `session_record` CHANGE filesize filesize BIGINT UNSIGNED NULL AFTER filepath;

CREATE TABLE `bookmark` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(36) NOT NULL,
  `description` varchar(63) DEFAULT '',
  `expression` varchar(512) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `bookmark_roles` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `bookmark_id` bigint(20) unsigned,
  `type` varchar(36) NOT NULL,
  `role` varchar(255) NOT null,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

ALTER TABLE terminal.bookmark_roles ADD CONSTRAINT fkey_bookmark_roles FOREIGN KEY (bookmark_id) REFERENCES terminal.bookmark(id) ON DELETE CASCADE;

#@v0.1.0.1-end@;

#@v0.2.2.1-begin@;

ALTER TABLE terminal.permission ADD expression TEXT NULL;

#@v0.2.2.1-end@;


#@v0.2.3.5-begin@;

CREATE TABLE `jump_server` (
  `id` varchar(36) NOT NULL,
  `name` varchar(63) NULL,
  `scope` varchar(512) NULL,
  `ip_address` varchar(36) NOT NULL,
  `port` int unsigned NOT null,
  `username` varchar(36) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `asset` (
  `id` varchar(36) NOT NULL,
  `name` varchar(63) NULL,
  `display_name` varchar(63) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `ip_address` varchar(36) NOT NULL,
  `port` int unsigned NOT null,
  `username` varchar(36) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
)
ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `sys_role` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `role_type` varchar(32) DEFAULT NULL COMMENT '角色类型',
  `is_system` varchar(8) DEFAULT 'no' COMMENT '是否系统角色',
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `sys_menu` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `display_name` varchar(64) DEFAULT NULL COMMENT '显示名',
  `url` varchar(255) DEFAULT NULL COMMENT '访问路径',
  `seq_no` int(11) DEFAULT '0' COMMENT '排序号',
  `parent` varchar(36) DEFAULT NULL COMMENT '父菜单',
  `is_active` varchar(8) DEFAULT 'yes' COMMENT '状态',
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `sys_user` (
  `id` varchar(36) NOT NULL COMMENT '主键',
  `display_name` varchar(64) DEFAULT NULL COMMENT '显示名',
  `password` varchar(128) DEFAULT NULL COMMENT '加密密钥',
  `salt` varchar(36) DEFAULT NULL COMMENT '加密盐',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `is_system` varchar(8) DEFAULT 'no' COMMENT '是否系统用户',
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `sys_role_menu` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` varchar(36) DEFAULT NULL COMMENT '角色id',
  `menu_id` varchar(36) DEFAULT NULL COMMENT '菜单id',
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sys_role_menu_ref_role` (`role_id`),
  KEY `sys_role_menu_ref_menu` (`menu_id`),
  CONSTRAINT `sys_role_menu_ref_menu` FOREIGN KEY (`menu_id`) REFERENCES `sys_menu` (`id`),
  CONSTRAINT `sys_role_menu_ref_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `sys_role_user` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `role_id` varchar(36) DEFAULT NULL COMMENT '角色id',
  `user_id` varchar(36) DEFAULT NULL COMMENT '用户id',
  `created_by` varchar(36) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `updated_by` varchar(36) DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sys_role_user_ref_role` (`role_id`),
  KEY `sys_role_user_ref_user` (`user_id`),
  CONSTRAINT `sys_role_user_ref_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`),
  CONSTRAINT `sys_role_user_ref_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO sys_menu (id,display_name,url,seq_no,parent,is_active,created_by,created_time,updated_by,updated_time) VALUES
	 ('system','系统',NULL,1,NULL,'yes','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('system_asset','终端管理',NULL,2,'system','yes','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('system_authorization','系统授权',NULL,4,'system','yes','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('system_audit','终端审计',NULL,3,'system','yes','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('terminal','终端',NULL,1,NULL,'yes','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('terminal_console','终端连接',NULL,2,'terminal','yes','admin','2021-08-26 00:00:00.0',NULL,NULL);

INSERT INTO sys_role (id,description,role_type,is_system,created_by,created_time,updated_by,updated_time) VALUES
	 ('CONFIG_ADMIN','配置管理员',NULL,'no','admin','2021-08-26 00:00:00.0',NULL,NULL),
   ('AUDIT_ADMIN','审计管理员',NULL,'no','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('CONSOLE_USER','终端用户',NULL,'no','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('SUPER_ADMIN','超级管理员',NULL,'yes','admin','2021-08-26 00:00:00.0',NULL,NULL);
     
INSERT INTO sys_user (id,display_name,password,salt,description,is_system,created_by,created_time,updated_by,updated_time) VALUES
	 ('admin','admin','69dcaa5aee6a462c5bbc5673c0e7cb4de2bcbf990ee75d4c4964400a','OZu*6u&OC})Ths5^','','yes','admin','2021-08-26 00:00:00.0',NULL,NULL);

INSERT INTO sys_role_user (role_id,user_id,created_by,created_time,updated_by,updated_time) VALUES
	 ('SUPER_ADMIN','admin','admin','2021-08-26 00:00:00.0',NULL,NULL);

INSERT INTO sys_role_menu (role_id,menu_id,created_by,created_time,updated_by,updated_time) VALUES
	 ('SUPER_ADMIN','system_asset','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('SUPER_ADMIN','system_authorization','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('SUPER_ADMIN','system_audit','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('SUPER_ADMIN','terminal_console','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('AUDIT_ADMIN','system_audit','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('CONFIG_ADMIN','system_asset','admin','2021-08-26 00:00:00.0',NULL,NULL),
	 ('CONSOLE_USER','terminal_console','admin','2021-08-26 00:00:00.0',NULL,NULL);

#@v0.2.3.5-end@;

