CREATE TABLE AudioTranscribeTracker(
	Id int PRIMARY KEY IDENTITY(1,1) NOT NULL,
	ClientId varchar(50) FOREIGN KEY REFERENCES Client(ClientId) NOT NULL,	
	AudioFileName  varchar(50) NOT NULL,
	AudioId  int FOREIGN KEY REFERENCES AudioTranscribe(Id) NOT NULL,
	ChunkSequence int NOT NULL,	
	ChunkText  varchar(max) NOT NULL,
	ChunkFilePath varchar(50) NOT NULL,
	ChunkTranscribeStart datetime,
	ChunkTranscribeEnd datetime,
	ChunkStatus  varchar(50) NOT NULL,
	ChunkCreatedDate datetime,
	Created datetime DEFAULT (GETDATE()) NOT NULL,
	Modified datetime DEFAULT (GETDATE()) NOT NULL,	
	IsActive bit DEFAULT 1,
	IsDeleted bit DEFAULT 0
	)