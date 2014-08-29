-- MySQL dump 10.11
--
-- Host: localhost    Database: ted
-- ------------------------------------------------------
-- Server version	5.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
CREATE TABLE `event` (
  `stamp` datetime NOT NULL default '1970-01-01 00:00:00',
  `duration` int(11) NOT NULL default '0',
  `watt` int(11) NOT NULL default '0',
  KEY `stamp` (`stamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `watt`
--

DROP TABLE IF EXISTS `watt`;
CREATE TABLE `watt` (
  `stamp` datetime NOT NULL default '1970-01-01 00:00:00',
  `watt` int(11) NOT NULL default '0',
  PRIMARY KEY  (`stamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `wattday`
--

DROP TABLE IF EXISTS `wattday`;
CREATE TABLE `wattday` (
  `stamp` datetime NOT NULL default '1970-01-01 00:00:00',
  `watt` int(11) NOT NULL default '0',
  PRIMARY KEY  (`stamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `watthour`
--

DROP TABLE IF EXISTS `watthour`;
CREATE TABLE `watthour` (
  `stamp` datetime NOT NULL default '1970-01-01 00:00:00',
  `watt` int(11) NOT NULL default '0',
  PRIMARY KEY  (`stamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `wattminute`
--

DROP TABLE IF EXISTS `wattminute`;
CREATE TABLE `wattminute` (
  `stamp` datetime NOT NULL default '1970-01-01 00:00:00',
  `watt` int(11) NOT NULL default '0',
  PRIMARY KEY  (`stamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table `watttensec`
--

DROP TABLE IF EXISTS `watttensec`;
CREATE TABLE `watttensec` (
  `stamp` datetime NOT NULL default '1970-01-01 00:00:00',
  `watt` int(11) NOT NULL default '0',
  PRIMARY KEY  (`stamp`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2008-09-17  0:11:33
