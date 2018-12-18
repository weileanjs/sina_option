# coding=utf-8
from config import MYSQL_CONFIG
import pymysql
from Log_Info.error_output import logError


connection_info = pymysql.connect(host=MYSQL_CONFIG['host'], port=MYSQL_CONFIG['port'], user=MYSQL_CONFIG['user'], password=MYSQL_CONFIG['password'],
                             db=MYSQL_CONFIG['db_info'],charset=MYSQL_CONFIG['charset'], cursorclass=pymysql.cursors.DictCursor)

connection_quote = pymysql.connect(host=MYSQL_CONFIG['host'], port=MYSQL_CONFIG['port'], user=MYSQL_CONFIG['user'], password=MYSQL_CONFIG['password'],
                             db=MYSQL_CONFIG['db_quote'],charset=MYSQL_CONFIG['charset'], cursorclass=pymysql.cursors.DictCursor)


def insert_t_stock_dict(*args):
    for connection in [connection_info,connection_quote]:
    # for connection in [connection_quote,]:
        try:
            connection.ping()
        except:
            connection.ping(True)
        try:
            cursor = connection.cursor()
            sql_to_dict = "INSERT INTO `t_stock_dict` (`name`, `code`, `market_id`, `sec_type`,  `dt_code`, `updatetime`, `is_close`) VALUES (%s ,%s ,%s ,%s ,%s ,%s ,%s );"
            # print(args[1],args[0][4:],args[0][:2],args[0][2:4],args[0],args[4] ,0)
            cursor.execute(sql_to_dict,(args[1],args[0][4:],args[0][:2],args[0][2:4],args[0],args[4] ,0))
            connection.commit()
        except Exception as e:
            if 'Duplicate' in str(e):
                pass
            else:
                logError('{} ERROR : {},  {}'.format(__name__,str(e),str(args)))
        finally:
            connection.close()



def insert_t_plate_type(*args):
    for connection in [connection_info,connection_quote]:
    # for connection in [connection_quote,]:
        try:
            connection.ping()
        except:
            connection.ping(True)
        try:
            cursor = connection.cursor()
            sql = " INSERT INTO `t_plate_type` (plate_dt_code, name ,type ,createtime , updatetime ) VALUES ( %s, %s, %s, %s, %s)"
            cursor.execute(sql,(args))
            connection.commit()
        except Exception as e:
            if 'Duplicate entry' in str(e):
                cursor = connection.cursor()
                sql = "UPDATE `t_plate_type` SET  updatetime='{}' WHERE plate_dt_code='{}'".format(args[4],args[0])
                cursor.execute(sql)
                connection.commit()
            else:
                logError('insert_t_plate_type ERROR : {},  {}'.format(str(e),str(args)))
        finally:
            connection.close()




def get_bk_stocks(type_id):
    connection = connection_info
    # connection = connection_quote
    try:
        connection.ping()
    except:
        connection.ping(True)
    cursor = connection.cursor()
    sql = " SELECT plate_dt_code FROM `t_plate_type`  WHERE type in {}".format(type_id)  # WHERE type=3
    cursor.execute(sql)
    tot = cursor.fetchall()
    return tot

def get_left_plate_dtcode(last_date):
    connection = connection_quote
    try:
        connection.ping()
    except:
        connection.ping(True)
    cursor = connection.cursor()
    sql = "SELECT plate_dt_code FROM t_plate_rela WHERE plate_dt_code LIKE '2020%' AND updatetime < '{}' GROUP BY plate_dt_code HAVING COUNT(*) > 10 ORDER BY plate_dt_code;".format(last_date)
    cursor.execute(sql)
    tot = cursor.fetchall()
    return tot




def insert_rela(*args):
    print(args)
    for connection in [connection_info,connection_quote]:
    # for connection in [connection_quote,]:
        try:
            connection.ping()
        except:
            connection.ping(True)
        cursor = connection.cursor()
        try:
            sql = " INSERT INTO `t_plate_rela` (plate_dt_code, stock_dt_code, createtime, updatetime) VALUES ( %s, %s, %s, %s)"
            cursor.execute(sql,(args))
            connection.commit()
        except Exception as e:
            if 'Duplicate entry' in str(e):
                sql = "UPDATE `t_plate_rela` SET updatetime='{}' WHERE plate_dt_code='{}' AND stock_dt_code='{}'".format(args[3],args[0],args[1])
                cursor.execute(sql)
                connection.commit()
            else:
                print(str(e))
                logError('{} ERROR : {},  {}'.format(__name__,str(e),str(args)))
        finally:
            connection.close()
