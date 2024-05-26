; ModuleID = "helloworld"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"(i32 %".1", i8** %".2")
{
entry:
  %".4" = getelementptr inbounds [6 x i8], [6 x i8]* @"var", i32 0, i32 0
  %".5" = getelementptr inbounds [4 x i8], [4 x i8]* @"println_0", i32 0, i32 0
  %".6" = call i32 @"puts"(i8* %".5")
  %".7" = getelementptr inbounds [4 x i8], [4 x i8]* @"println_1", i32 0, i32 0
  %".8" = call i32 @"puts"(i8* %".7")
  ret i32 0
}

declare i32 @"puts"(i8* %".1")

declare i32 @"strlen"(i8* %".1")

@"var" = constant [6 x i8] c"\22bar\22\00"
@"println_0" = constant [4 x i8] c"foo\00"
@"println_1" = constant [4 x i8] c"bar\00"