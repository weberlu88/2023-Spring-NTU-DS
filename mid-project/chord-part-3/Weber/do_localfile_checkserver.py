import os
from flask import Flask, request

app = Flask(__name__)
dirname = os.path.dirname(__file__)    # 取得 py 檔的路徑
fsdir = os.path.join(dirname, 'files') # 將 FS 路徑設好

@app.route('/file_exists', methods=['GET'])
def check_file_exists():
    ''' 判斷 filename 參數是否存在檔案系統 '''
    filename = request.args.get('filename')
    if os.path.isfile(os.path.join(fsdir, filename)):
        return {'file_exists': True}
    return {'file_exists': False}
    
@app.route('/list_files', methods=['GET'])
def list_files():
    ''' 列出檔案系統中的檔案 '''
    files = []
    for file in os.listdir(fsdir):
        if os.path.isfile(os.path.join(fsdir, file)):
            files.append(file)
    print('list_files', files)
    return {'files': files}

if __name__ == '__main__':
    list_files()  # test list file function
    app.run(host='0.0.0.0', port=9999, debug=True)
    # files = []
    # dirname = os.path.dirname(__file__)
    # fsdir = os.path.join(dirname, 'files')
    # for file in os.listdir(fsdir):
    #     if os.path.isfile(os.path.join(fsdir, file)):
    #         files.append(file)
    # print(files)
    
    # for file in os.listdir('./Weber/files'):
    #     if os.path.isfile(os.path.join('./Weber/files', file)):
    #         files.append(file)
    # print(files)

    # dirname = os.path.dirname(__file__)
    # filename = os.path.join(dirname, 'files/aaa.txt')
    # print(dirname)
    # print(filename)