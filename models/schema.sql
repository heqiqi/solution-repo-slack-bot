
CREATE TABLE `conversation_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL COMMENT '用户的login',
  `channel` varchar(256) NOT NULL COMMENT 'channel',
  `thread_ts` varchar(256) NOT NULL COMMENT '用户的login',
  `message` text NOT NULL COMMENT '对话内容',
  `createAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modifyAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `version` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `thread_ts_index` (`thread_ts`),
  KEY `channel_index` (`channel`)
)

CREATE TABLE `resolved_request` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL COMMENT '用户的login',
  `thread_ts` varchar(256) NOT NULL COMMENT 'thread TS',
  `message` text NOT NULL COMMENT '对话内容',
  `createAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modifyAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `version` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `thread_ts_index` (`thread_ts`)
);

CREATE TABLE `need_help` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(128) NOT NULL COMMENT '用户的login',
  `industry` varchar(256) NOT NULL COMMENT '行业',
  `scenario` text NOT NULL COMMENT '场景',
  `createAt` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modifyAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `version` int DEFAULT NULL,
  PRIMARY KEY (`id`)
);