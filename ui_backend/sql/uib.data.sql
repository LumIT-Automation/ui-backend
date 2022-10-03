-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Creato il: Mag 06, 2021 alle 16:58
-- Versione del server: 10.3.27-MariaDB-0+deb10u1-log
-- Versione PHP: 7.3.27-1~deb10u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `uib`
--

--
-- Dump dei dati per la tabella `privilege`
--

INSERT INTO `privilege` (`id`, `privilege`, `privilege_type`, `description`) VALUES
(1, 'permission_identityGroups_get', 'global', NULL),
(2, 'permission_identityGroups_post', 'global', NULL),
(3, 'permission_roles_get', 'global', NULL),
(4, 'permission_identityGroup_patch', 'global', NULL),
(5, 'permission_identityGroup_delete', 'global', NULL),
(6, 'workflows_get', 'object', NULL),
(7, 'workflow_put', 'object', NULL);

--
-- Dump dei dati per la tabella `role`
--

INSERT INTO `role` (`id`, `role`, `description`) VALUES
(1, 'admin', 'admin'),
(2, 'staff', 'read / write, excluding assets'),
(3, 'readonly', 'readonly');

--
-- Dump dei dati per la tabella `role_privilege`
--

INSERT INTO `role_privilege` (`id_role`, `id_privilege`) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 6),
(1, 7),
(2, 6),
(2, 7);


COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
