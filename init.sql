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


#@v0.2.3.1-begin@;

CREATE TABLE terminal.jump_server (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
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

#@v0.2.3.1-end@;

