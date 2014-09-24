import psycopg2

def population_query(country):
    try:
        cnxn = psycopg2.connect(host='ivlabsdssql01.na.corp.intven.com', port=5432, dbname='idm_db')
    except pycopg2.Error:
        raise Exception("Failed connection to %s." % server_name)

    cursor = cnxn.cursor()
    data = (country,)
    SQL  =  """
    select dot_name, ansii_name, hid_level, hierarchy_name_id, parentid, hierarchy_name_set_id, shape_id, shape_set_id, shape_class, valid_from, valid_to, raster_notes, (st_stats_all).sum as st_stats_sum_population
    from
    (
        select dot_name, ansii_name, hid_level, hierarchy_name_id, parentid, hierarchy_name_set_id, shape_id, shape_set_id, shape_class, valid_from, valid_to, cast('afripop_30_2010_adj summary 20140714' as text) as raster_notes, ST_SummaryStats(ST_UNION(ST_Clip(rast, geom))) as st_stats_all
        from  raster.afripop_30_2010_adj,
        (
        select dot_name, valid_from, valid_to, a.hid_level, a.parentid, b.*, ansii_name, geom from
            sd.hierarchy_name_table a join sd.hierarchy_name_shape_map b on (a.id = b.hierarchy_name_id)
            join sd.shape_table c on (b.shape_id = c.id)
        where a.hierarchy_name_set_id=1 and a.hid_level in (3,4,5) and valid_to > now() and
            a.id in (select id from
    (select id, row_number() over (partition by 1) as rn from sd.hierarchy_name_table where hierarchy_name_set_id in (1,6) and hid_level in (3,4,5) and lower(dot_name) like %s) tmp
    where rn <=6000)
        ) as t1
        where ST_Intersects(rast, geom)
        group by dot_name, ansii_name, hierarchy_name_id, hierarchy_name_set_id, shape_id, shape_set_id, shape_class, valid_from, valid_to, hid_level, parentid
        ) z
        order by hierarchy_name_set_id, hid_level, dot_name
    ;"""

    cursor.execute(SQL, data)

    for row in cursor:
        print(row)
    cnxn.close()

population_query('africa:liberia%')