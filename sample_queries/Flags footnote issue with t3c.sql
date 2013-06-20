
/* Flags footnote issue with t3c */

select sum(close_today) as sum, item from t3c
group by item
order by sum desc
/* all the items where sum field is null are stray footnotes that populated as items */

/*
SELECT date, item, close_today from t3c
where item like '%subject to limit%' OR item like '%statutory debt limit%'
*/

