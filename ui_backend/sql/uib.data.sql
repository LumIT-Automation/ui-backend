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
-- Dump dei dati per la tabella `workflow`
--

INSERT INTO `workflow` (`id`, `name`, `technologies`, `description`) VALUES
(1, 'flow_test1', 'f5,infoblox,checkpoint', 'test workflow'),
(2, 'flow_test2', 'f5,infoblox', 'test workflow'),
(3, 'checkpoint_add_host', 'infoblox,checkpoint', 'add checkpoint host workflow'),
(4, 'checkpoint_remove_host', 'infoblox,checkpoint', 'remove checkpoint host workflow'),
(5, 'flow_test3', 'f5,infoblox', 'test workflow');


COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
