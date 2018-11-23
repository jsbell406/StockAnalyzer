BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `stock_name` (
	`stock_ticker`	TEXT,
	`stock_name`	TEXT
);
CREATE TABLE IF NOT EXISTS `stock_article` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`stock_ticker`	TEXT NOT NULL,
	`url`	TEXT NOT NULL,
	`publish_date`	TEXT,
	`article_score`	REAL,
	`save_date`	TEXT
);
CREATE TABLE IF NOT EXISTS `agg_score_stock_article_xref` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`agg_score`	INTEGER,
	`stock_article`	INTEGER,
	`score_date`	TEXT
);
CREATE TABLE IF NOT EXISTS `agg_score` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	`stock_ticker`	TEXT NOT NULL,
	`avg_score`	REAL,
	`max_score`	REAL,
	`min_score`	REAL,
	`score_date`	TEXT
);
CREATE TRIGGER trg_stock_article_save_date 
AFTER INSERT ON stock_article 
BEGIN 
	UPDATE stock_article 
	SET save_date = date('now') 
	WHERE stock_article.id = NEW.id; 
END;
CREATE TRIGGER trg_agg_score_stock_article_date
AFTER INSERT ON agg_score_stock_article_xref
BEGIN
    UPDATE agg_score_stock_article_xref
    SET score_date = date('now')
    WHERE agg_score_stock_article_xref.id = NEW.id;
END;
CREATE TRIGGER trg_agg_score_date
AFTER INSERT ON agg_score
BEGIN
    UPDATE agg_score
    SET score_date = date('now')
    WHERE agg_score.id = NEW.id;
END;
COMMIT;
