// newmpq <out.mpq> <dir> file1 file2 ...
// Creates a new MPQ v1 (zlib + listfile) with the given files and verifies they read back identical.
// "war3map.j" is stored as "scripts\war3map.j".
#include "StormLib.h"
#include <cstdio>
#include <string>
#include <vector>
static std::vector<char> slurp(const std::string& p){ std::vector<char> b; FILE* f=fopen(p.c_str(),"rb"); if(!f) return b; fseek(f,0,SEEK_END); long n=ftell(f); fseek(f,0,SEEK_SET); b.resize(n); if(n && fread(b.data(),1,n,f)!=(size_t)n) b.clear(); fclose(f); return b; }
static std::string mpqname(const std::string& n){ return n=="war3map.j" ? "scripts\\war3map.j" : n; }
int main(int argc, char** argv){
  if(argc<4){ printf("usage: newmpq out.mpq dir files...\n"); return 2; }
  HANDLE h; if(!SFileCreateArchive(argv[1], MPQ_CREATE_LISTFILE | MPQ_CREATE_ARCHIVE_V1, 64, &h)){ printf("create error %d\n",SErrGetLastError()); return 1; }
  for(int i=3;i<argc;i++){ std::string local=std::string(argv[2])+"/"+argv[i];
    if(!SFileAddFileEx(h, local.c_str(), mpqname(argv[i]).c_str(), MPQ_FILE_COMPRESS|MPQ_FILE_REPLACEEXISTING, MPQ_COMPRESSION_ZLIB, MPQ_COMPRESSION_NEXT_SAME)){ printf("add error %s %d\n",argv[i],SErrGetLastError()); return 1; } }
  SFileCloseArchive(h);
  if(!SFileOpenArchive(argv[1],0,STREAM_FLAG_READ_ONLY,&h)){ printf("reopen error\n"); return 1; }
  for(int i=3;i<argc;i++){ std::vector<char> want=slurp(std::string(argv[2])+"/"+argv[i]); HANDLE fh;
    if(!SFileOpenFileEx(h, mpqname(argv[i]).c_str(), 0, &fh)){ printf("missing %s\n",argv[i]); return 1; }
    DWORD sz=SFileGetFileSize(fh,NULL); std::vector<char> got(sz); DWORD rd=0; if(sz) SFileReadFile(fh,got.data(),sz,&rd,NULL); SFileCloseFile(fh);
    if(rd!=want.size() || got!=want){ printf("mismatch %s\n",argv[i]); return 1; } }
  SFileCloseArchive(h); printf("ok %d files verified\n", argc-3); return 0; }
