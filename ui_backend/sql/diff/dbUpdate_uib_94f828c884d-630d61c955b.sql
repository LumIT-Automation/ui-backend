
/*
OLD COMMIT: 94f828c884d0e9d83ee56706c6b3693a2f184a94
NEW COMMIT: 630d61c955be7c32d8c42bf63da1a1a31592be43
*/


/*
SQL SCHEMA SECTION
*/

## mysqldiff 0.60
## 
## Run on Mon Dec  2 17:19:04 2024
## Options: debug=0, password=password, user=uib, host=10.0.111.12
##
## --- file: /tmp/uib_old.sql
## +++ file: /tmp/uib_new.sql

DROP TABLE group_role_workflow;

DROP TABLE identity_group;

DROP TABLE privilege;

DROP TABLE role;

DROP TABLE role_privilege;

DROP TABLE workflow;

CREATE TABLE `workflow` (
  `id` int(11) NOT NULL,
  `name` varchar(64) NOT NULL,
  `technologies` SET('f5', 'infoblox', 'vmware', 'checkpoint'),
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*
DATA SECTION
*/

set foreign_key_checks = 0;

INSERT INTO `workflow` (`id`, `name`, `technologies`, `description`) VALUES
(1, 'flow_test1', 'f5,infoblox,checkpoint', 'test workflow'),
(2, 'flow_test2', 'f5,infoblox,checkpoint', 'test workflow'),
(3, 'checkpoint_add_host', 'infoblox,checkpoint', 'add checkpoint host workflow'),
(4, 'checkpoint_remove_host', 'infoblox,checkpoint', 'remove checkpoint host workflow'),
(5, 'cloud_account', 'infoblox,checkpoint', 'cloud account workflow');

set foreign_key_checks = 1;
