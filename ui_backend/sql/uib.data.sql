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

INSERT INTO `privilege` (`id`, `privilege`, `description`) VALUES
(1, 'exec', 'Can execute workflow');

--
-- Dump dei dati per la tabella `role`
--

INSERT INTO `role` (`id`, `role`, `description`) VALUES
(1, 'exec', '');

--
-- Dump dei dati per la tabella `role_privilege`
--

INSERT INTO `role_privilege` (`id_role`, `id_privilege`) VALUES
(1, 1);

--
-- Dump dei dati per la tabella `workflow`
--

INSERT INTO `workflow` (`id`, `name`, `description`) VALUES
(1, 'checkpoint_remove_host', 'CheckPoint remove host, with Infoblox information fetching'),
(2, 'checkpoint_add_host', 'CheckPoint add host, with Infoblox information fetching');


COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
