CREATE TABLE SentimentAnalysis(
	Id int PRIMARY KEY IDENTITY(1,1) NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,	
	TranscriptId  int FOREIGN KEY REFERENCES AudioTranscribe(Id) NOT NULL,
	SentimentScore  varchar(50) NOT NULL,
	SentimentLabel  varchar(max) NOT NULL,
	AnalysisDateTime  varchar(50) NOT NULL,
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,
	IsActive bit DEFAULT 1,
	IsDeleted bit DEFAULT 0
	)