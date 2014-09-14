import MySQLdb
# logging is inside our package (ted1k),
from logging import logInfo,logWarn,logError


# Config - Should inject variable from env, with defaults
# the variable formats are from docker links
MYSQL_PORT_3306_TCP_ADDR = '172.17.42.1'
# MYSQL_PORT_3306_TCP_PORT = '3306'
MYSQL_ENV_MYSQL_DATABASE = 'ted'

class MySQL:
    conn = None

    def connect(self):
        self.conn = MySQLdb.connect (host = MYSQL_PORT_3306_TCP_ADDR,db=MYSQL_ENV_MYSQL_DATABASE)

    def close(self):
        if self.conn != None:
            self.conn.close()
            self.conn = None

    def cursor(self):
        if self.conn is None:
            self.connect()
        return self.conn.cursor()

    def executeQuery(self,query):
        cursor = self.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def getOneRow(self,sql):
        cursor = self.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        return row

    def getScalar(self,sql):
        cursor = self.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        cursor.close()
        if row is None: return None
        return row[0]

    def tableExists(self,tablename):
        exists = self.getScalar("show tables like '%s'" % tablename) is not None
        return exists
        
    def checkOrCreateTable(self,tablename):
        exists = self.tableExists(tablename)
        if exists:
                logInfo(" Table %s is OK" % (tablename))
                return

        ddl = """CREATE TABLE %s (
stamp datetime NOT NULL default '1970-01-01 00:00:00',
watt int(11) NOT NULL default '0',
PRIMARY KEY %sByStamp (stamp)
);
""" % (tablename,tablename)
        cursor = self.cursor()
        cursor.execute(ddl)
        cursor.close()
        logInfo(" Created %s table" % (tablename))

    # For use with with! Allows cleaning up the connection
    # Not yet tested
    def __enter__(self):
        # logInfo('Entering MySQL')
        return self
    def __exit__(self, type, value, traceback):
        # logInfo('Exiting MySQL')
        self.close()
