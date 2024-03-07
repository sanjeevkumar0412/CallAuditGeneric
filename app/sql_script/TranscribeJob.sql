CREATE TABLE TranscribeJob(
	Id int PRIMARY KEY IDENTITY(1,1) NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,	
	JobStarttime  datetime NOT NULL,
	JobEndTime  datetime NOT NULL,
	IsError  bit DEFAULT 0,	
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,
	IsActive bit DEFAULT 1,
	IsDeleted bit DEFAULT 0
	)