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
