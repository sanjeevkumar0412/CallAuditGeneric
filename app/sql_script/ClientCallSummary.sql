CREATE TABLE ClientCallSummary(
	Id int  PRIMARY KEY IDENTITY(1,1) NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,		
	SummaryDescription  varchar(max) NOT NULL,
	SummaryDateTime datetime NOT NULL,	
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,
	IsActive bit DEFAULT 1,
	IsDeleted bit DEFAULT 0
	)