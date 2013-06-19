/*Avg Federal Reserve Account Balance by month of the year */

select avg(close_today) as average_close, strftime('%Y-%m',date) as YearMonth, account as account from t1
where account = 'Federal Reserve Account'
group by strftime('%Y-%m',date), account
order by strftime('%Y-%m',date)