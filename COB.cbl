       IDENTIFICATION DIVISION.
       PROGRAM-ID. COB.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT INFILE ASSIGN TO INP
           ORGANIZATION IS SEQUENTIAL
           ACCESS IS SEQUENTIAL
           FILE STATUS FS1.
           SELECT OUTFILE1 ASSIGN TO OUT1
           ORGANIZATION IS SEQUENTIAL
           ACCESS IS SEQUENTIAL
           FILE STATUS FS2.           
           SELECT OUTFILE2 ASSIGN TO OUT2
           ORGANIZATION IS SEQUENTIAL
           ACCESS IS SEQUENTIAL
           FILE STATUS FS3.       
       DATA DIVISION.
       FILE SECTION.
       FD INFILE.
       01 INREC.
           05 I-TRAN-ID PIC X(5).
           05 I-TRAN-DATE PIC X(10).
           05 I-TRAN-DESC PIC X(10).
           05 I-TRAN-AMT PIC 9(10).
       FD OUTFILE1.
       01 OUTREC1.
           05 O1-TRAN-ID PIC X(5).
           05 O1-TRAN-DATE PIC X(10).
           05 O1-TRAN-DESC PIC X(10).
           05 O1-TRAN-AMT PIC 9(10).
       FD OUTFILE2.
       01 OUTREC2.
           05 O2-TRAN-ID PIC X(5).
           05 O2-TRAN-DATE PIC X(10).
           05 O2-TRAN-DESC PIC X(10).
           05 O2-TRAN-AMT PIC 9(10).     
       WORKING-STORAGE SECTION.
       01 FS1 PIC 9(2).             
       01 FS2 PIC 9(2).
       01 FS3 PIC 9(2).
       PROCEDURE DIVISION.
       000-MAIN-PARA.
           PERFORM 000-OPEN-PARA THRU
           000-OPEN-PARA-EXIT
           PERFORM 000-READ-PARA THRU
           000-READ-PARA-EXIT
           PERFORM 000-CLOSE-PARA THRU
           000-CLOSE-PARA-EXIT
           PERFORM 000-TERM-PARA.
       000-MAIN-PARA-EXIT.
           EXIT.         
       000-OPEN-PARA.
           OPEN INPUT INFILE.
           OPEN OUTPUT OUTFILE1 OUTFILE2.
           EVALUATE TRUE 
                  WHEN FS1 = 0 
                         DISPLAY "INP FILE OPENED"
                  WHEN OTHER
                         DISPLAY "FILE NOT OPENED " FS1 
           END-EVALUATE.
           EVALUATE TRUE 
                  WHEN FS2 = 0 
                         DISPLAY "OUTFILE1 OPENED"
                  WHEN OTHER
                         DISPLAY "FILE NOT OPENED " FS2
           END-EVALUATE.
           EVALUATE TRUE 
                  WHEN FS3 = 0 
                         DISPLAY "OUTFILE2 OPENED"
                  WHEN OTHER
                         DISPLAY "FILE NOT OPENED " FS3 
           END-EVALUATE.  
       000-OPEN-PARA-EXIT.
           EXIT.
       000-READ-PARA. 
           READ INFILE.
           EVALUATE TRUE 
                  WHEN FS1 = 0 
                         DISPLAY "INFILE READED"
                  IF I-TRAN-AMT > 20000
                         MOVE INREC TO OUTREC1
                         WRITE OUTREC1
                         DISPLAY "RECORD MOVED TO OUTREC1"
                  ELSE 
                         MOVE INREC TO OUTREC2
                         WRITE OUTREC2
                         DISPLAY "RECORD MOVED TO OUTREC2"  
                  END-IF    
                  WHEN OTHER
                         DISPLAY "FILE NOT READED " FS1 
                         STOP RUN
           END-EVALUATE.  
       000-READ-PARA-EXIT.
           EXIT.
       000-CLOSE-PARA.
           CLOSE INFILE OUTFILE1 OUTFILE2.
       000-CLOSE-PARA-EXIT.
           EXIT.
       000-TERM-PARA.
           STOP RUN.
           

