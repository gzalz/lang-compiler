; ModuleID = "helloworld"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"(i32 %".1", i8** %".2")
{
entry:
  %".4" = getelementptr inbounds [9 x i8], [9 x i8]* @"println_0", i32 0, i32 0
  %".5" = getelementptr inbounds [9 x i8], [9 x i8]* @"println_1", i32 0, i32 0
  %".6" = call i32 @"puts"(i8* %".4")
  %".7" = call i32 @"puts"(i8* %".5")
  ret i32 0
}

@"println_0" = constant [9 x i8] c"\22Line 1\22\00"
@"println_1" = constant [9 x i8] c"\22Line 2\22\00"
declare i32 @"puts"(i8* %".1")
