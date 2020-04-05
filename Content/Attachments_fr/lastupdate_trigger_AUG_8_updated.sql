

ALTER PROCEDURE [dbo].[ActivateSearchIndexes]
	
@groupid int,
	
@type tinyint = null,
	
@islocked bit = null,
	
@active bit

AS

BEGIN
	
   IF (@active = 0)
	
    BEGIN
		
     UPDATE searchindex SET active = 0, lastUpdate=GETDATE()
		
     WHERE groupnum = @groupid 
		      
           AND [Type]=ISNULL(@type,[Type]) AND IsLocked=ISNULL(@islocked,IsLocked)
	
    END
	
   ELSE
	
    BEGIN
		
     UPDATE searchindex SET active = 1, Type = 2, IsLocked = 0,lastUpdate=GETDATE()
		
     WHERE groupnum = @groupid 
		      
     AND IsLocked=ISNULL(@islocked,IsLocked)  
	
    END

END




Alter PROCEDURE [dbo].[Stp_IndexStatus_Set]
	 @indexpath varchar(260) = null,
	 @indexid int = null,
	 @active bit
AS
BEGIN
SET NOCOUNT ON
	
	 select indexid into #idx
	 from searchindex (nolock)
	 where indexid = @indexid or indexpath=@indexpath
	 
	 create clustered index ixx_x on #idx(indexid)
	 
	 declare @idx int
	 set @idx =0
	 
	 while (1=1)
	 begin
		select TOP 10 indexID 
		into #i		
		from #idx
		where indexid>@idx
		order by indexid
		
		if @@ROWCOUNT = 0 break
		
		update searchindex
			set active=@active,
			lastUpdate=GETDATE()
		where indexid in (select indexid from #i)
		
		select @idx=MAX(indexid) from #i
		drop table #i
		
	 end
	 
	 if (@indexid is null)
		select @indexid=indexid 
		from searchindex (Nolock) where indexpath=@indexpath
		option (maxdop 1)
		
	 select @indexid
END
GO

ALTER PROCEDURE [dbo].[adm_UnloadActiveIndexesFromMemory]
	@WaitSecond int = 30
AS

SELECT	indexid INTO #tmp FROM searchindex WHERE active = 1
UPDATE	s
   SET	active = 0,lastUpdate=GETDATE()
  FROM	#tmp t join searchindex s on (t.indexid = s.indexid)
  
WAITFOR DELAY '00:01:00'

UPDATE	s
   SET	active = 1,lastUpdate=GETDATE()

  FROM	#tmp t join searchindex s ON (t.indexid = s.indexid)

SELECT * FROM vw_ActiveIndex


Alter PROC [dbo].[Stp_SearchIndex_ActivateReMergedIndexes]
(
@GroupID INT
)
AS
BEGIN
  UPDATE SearchIndex 
  SET 
  [Type]=2,
  lastUpdate = GETDATE()  
  WHERE 
  Active=1 AND 
  [Type]=3 AND 
  groupnum=@GroupID
END

GO

ALTER PROCEDURE [dbo].[ResetIndexDocCount]
	@indexid int
AS
BEGIN
	UPDATE searchindex SET active = 0, DocCount = 0,SizeInMB=0,lastUpdate=GETDATE() 
        WHERE indexid = @indexid
END
GO

ALTER PROCEDURE [dbo].[CreateIndex]
	@indexpath varchar(260),
	@type tinyint,
	@leaseseconds int,
	@groupnum int=-1,
	@DocCount int,
	@SizeinMB decimal(10,4)=NULL,
	@indexid int OUT
AS
begin
	declare @active bit
	set @active=0
	select @indexid=indexid,@active=active from searchindex (nolock) where indexpath=@indexpath and type=@type
	if (@@rowcount = 0)
	begin
		INSERT INTO searchindex (indexpath,type,leaseseconds,groupnum,active,DocCount,lastUpdate,SizeInMB) VALUES(@indexpath,@type,@leaseseconds,@groupnum,@active,@DocCount,GETDATE(),@SizeinMB)
		SET @indexid = SCOPE_IDENTITY()
	end
	else
	begin
		--if( @active=0)
		--begin
			update searchindex set active=1, DocCount=@DocCount , SizeInMB=@SizeinMB,lastUpdate=GETDATE() where indexpath=@indexpath and type=@type 
		--end
	end
end
GO


ALTER PROCEDURE [dbo].[Stp_IndexStatus_Set]
	 @indexpath varchar(260) = null,
	 @indexid int = null,
	 @active bit
AS
BEGIN
SET NOCOUNT ON
	
	 select indexid into #idx
	 from searchindex (nolock)
	 where indexid = @indexid or indexpath=@indexpath
	 
	 create clustered index ixx_x on #idx(indexid)
	 
	 declare @idx int
	 set @idx =0
	 
	 while (1=1)
	 begin
		select TOP 10 indexID 
		into #i		
		from #idx
		where indexid>@idx
		order by indexid
		
		if @@ROWCOUNT = 0 break
		
		update searchindex
			set active=@active,
			lastUpdate=GETDATE()
		where indexid in (select indexid from #i)
		
		select @idx=MAX(indexid) from #i
		drop table #i
		
	 end
	 
	 if (@indexid is null)
		select @indexid=indexid 
		from searchindex (Nolock) where indexpath=@indexpath
		option (maxdop 1)
		
	 select @indexid
END
GO

ALTER PROCEDURE [dbo].[Stp_SearchIndex_CreateIndex]
	@indexpath varchar(260),
	@type tinyint,
	@leaseseconds int,
	@groupnum int=-1,
	@DocCount int,
	@SizeinMB decimal(10,4)=NULL,	
	@active bit,
	@indexid int OUT
AS
begin
	
	select @indexid=indexid from searchindex (nolock) where indexpath=@indexpath
	if (@@rowcount = 0)
	begin
		INSERT INTO searchindex (indexpath,type,leaseseconds,groupnum,active,DocCount,lastUpdate,SizeInMB) VALUES(@indexpath,@type,@leaseseconds,@groupnum,@active,@DocCount,GETDATE(),@SizeinMB)
		SET @indexid = SCOPE_IDENTITY()
	end
	else
	begin
		--if( @active=0)
		--begin
			update searchindex 
			set 
			indexpath = @indexpath,
			[Type] = @type,
			active=@active, 
			DocCount=ISNULL(@DocCount, DocCount), 
			SizeInMB=ISNULL(@SizeinMB, SizeinMB),
			lastUpdate = GETDATE()			
			where indexid = @indexid
		--end
	end
end
GO

ALTER PROC [dbo].[Stp_SearchIndex_DeActivateRebuildedIndexes]
(
@AppType TINYINT, 
@GroupID int
)
AS
BEGIN
  UPDATE SearchIndex 
  SET 
  Active=0,
  lastUpdate = GETDATE()  
  WHERE 
  Active=1 AND 
  IsLocked=1 AND 
  AppType=@AppType AND 
  groupnum=@GroupID
END
GO

ALTER PROCEDURE [dbo].[UpdateSearchIndex]
	@indexid int,
	@indexpath varchar(260),
	@groupid int,
	@type tinyint,
	@leasesecs int,
	@active bit,
	@doccount int,
	@islocked bit
AS
BEGIN
	update searchindex
	set indexpath = @indexpath,
	groupnum = @groupid,
	type = @type,
	LeaseSeconds = @leasesecs,
	active = @active,
	DocCount = @doccount,
	islocked = @islocked,
	lastUpdate=GETDATE()
	where indexid = @indexid
END
GO

