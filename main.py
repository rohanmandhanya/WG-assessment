from fastapi import FastAPI, HTTPException
import argparse
import uvicorn
from pathlib import Path
import stat
import pwd



root_directory = Path("/")
app = FastAPI()


def file_info(path: Path):
    try:
        stat_info = path.stat()
        return {
            "name": path.name,
            "owner": pwd.getpwuid(stat_info.st_uid).pw_name,
            "size": stat_info.st_size,
            "permissions": oct(stat.S_IMODE(stat_info.st_mode))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{full_path:path}")
def browsable(full_path: str):

    full_path = full_path[1:]

    target_path = root_directory / Path(full_path)

    if target_path.is_dir():
        contents = []

        for file in target_path.iterdir():

            contents.append(file_info(file))

        return {"contents": contents}

    if target_path.is_file():
        try:
            with open(target_path) as f:
                return {"name": target_path.name, "contents": f.read()}
        except Exception as e:
            raise HTTPException(detail="Bad file")

    raise HTTPException(status_code=400, detail="Invalid file path")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a file browser API.")
    parser.add_argument("--root", type=str, help="Root directory to serve files from")
    args = parser.parse_args()
    
    root_directory = Path(args.root).resolve()
    if not root_directory.is_dir():
        print("Error: Provided root path is not a directory.")
        exit(1)

    uvicorn.run(app, host="0.0.0.0", port=8000)