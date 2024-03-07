CREATE TABLE AudioTranscribe(
	Id int PRIMARY KEY IDENTITY(1,1) NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,	
	AudioFileName varchar(50) NOT NULL,
	JobStatus  varchar(50) NOT NULL,
	FileType  varchar(50) NOT NULL,
	TranscribeText  varchar(max) NOT NULL,
	TranscribeFilePath varchar(50) NOT NULL,
	TranscribeStartTime datetime,
	TranscribeEndTime datetime,	
	TranscribeDate datetime DEFAULT (GETDATE()) NOT NULL,
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,
	IsActive bit DEFAULT 1,
	IsDeleted bit DEFAULT 0
	)