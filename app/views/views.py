from app import app
from flask import render_template, request, url_for, redirect
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os

UPLOAD_FILES = "app/input/"
df = None
size = None
colname = None
head = None
describe = None
corr = None
isnull = None
btn_path = None
res_code = None
heat_path = None

hist_url = None
scatter_url = None

def getResult():
    global size
    global colname
    global head
    global describe
    global corr
    global isnull
    global btn_path
    global res_code
    return [size, colname, head, describe, corr, isnull, btn_path, res_code]


def createHist(col):
    global df
    savepath = "app/static/histogram/"+col+".png"
    url = "../static/histogram/"+col+".png"
    try:
        desc_col = df.describe().columns.values
        print("DESC col: ", desc_col)
        if col in desc_col:
            data = df[col]
            plt.figure()
            data.hist(edgecolor="k")
            plt.xlabel(col)
            plt.ylabel("Frequency")
            plt.title("Histogram of "+col, fontsize=16)
            plt.tight_layout()
            plt.savefig(savepath)
            plt.close("all")
        else:
            data = df[col]
            plt.figure()
            ax = data.value_counts().plot(kind="barh", title="Count plot of "+col, rot=45)
            ax.set_xlabel("Counts")
            ax.set_ylabel(col)
            plt.tight_layout()
            plt.savefig(savepath)
            plt.close("all")
        return url
    except:
        return redirect(url_for('index'))

def createScatter(xcol, ycol):
    global df
    savepath = "app/static/scatter/"+xcol+"_"+ycol+".png"
    url = "../static/scatter/"+xcol+"_"+ycol+".png"
    try:
        plt.figure()
        df.plot.scatter(x=xcol, y=ycol)
        plt.xlabel(xcol)
        plt.ylabel(ycol)
        plt.title(xcol+" × "+ycol, fontsize=16)
        plt.tight_layout()
        plt.savefig(savepath)
        plt.close("all")
        return url
    except:
        return "エラーが発生しました"

def codeInfo(head, describe, corr, isnull):
    head = head.to_html()
    describe = describe.to_html()
    corr = corr.to_html()
    isnull = isnull.to_html()
    return [head, describe, corr, isnull]

def createInfo(path):
    print("PATH2: ", path)
    global df
    global heat_path
    heatfiles = os.listdir("app/static/heatmap")
    heatfiles = "".join(heatfiles)
    corr_file = re.findall("\d*", heatfiles)
    corr_file = [int(num) for num in corr_file if not num == ""]
    print(corr_file)
    if not corr_file:
        corr_file.append(0)
    max_path = max(corr_file)
    print("MAX PATH: ", max_path)
    print("データフレーム代入前: ", df)
    print(os.getcwd())
    df = pd.read_csv(path)
    print("データフレーム代入後: ", df)
    size_f = df.shape
    colname_f = df.columns.values
    head = df.head(10)
    describe = df.describe()
    corr = df.corr()
    print(corr)
    #すでに画像番号が存在していた場合
    if max_path in corr_file:
        max_path += 1
        heat_path = "app/static/heatmap/img"+str(max_path)+".png"
        plt.figure()
        sns.heatmap(df.corr())
        plt.tight_layout()
        plt.savefig(heat_path)
        print("クローズします")
        plt.close("all")
    btn_path = "../static/heatmap/img"+str(max_path)+".png"
    print("result.htmlからのパスは", btn_path)
    isnull = pd.DataFrame(df.isnull().sum(), columns=["Null Count"])
    head_f, describe_f, corr_f, isnull_f = codeInfo(head, describe, corr, isnull)
    res_code = """
                #Size<br>
                print("*"*60)<br>
                print(.shape)<br>
                #Columns<br>
                print("-"*60)<br>
                print(.columns.values)<br>
                #Heading<br>
                print("-"*60)<br>
                print(.head(10))<br>
                #Describe<br>
                print("-"*60)<br>
                print(.describe())<br>
                #Correration<br>
                print("-"*60)<br>
                print(.corr())<br>
                #Is null<br>
                print("-"*60)<br>
                print(.isnull().sum())<br>
                print("*"*60)<br>
    """
    return [size_f, colname_f, head_f, describe_f, corr_f, isnull_f, btn_path, res_code]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST", "GET"])
def getInfo():
    global size
    global colname
    global head
    global describe
    global corr
    global isnull
    global btn_path
    global res_code
    global UPLOAD_FILES
    if request.method == "POST":
        try:
            data = request.files["data"]
            filename = data.filename
            savepath = UPLOAD_FILES+filename
            print("SAVE PATH: ", savepath)
            data.save(savepath)
            size, colname, head, describe, corr, isnull, btn_path, res_code = createInfo(savepath)
            print("ボタンからのパス最終確認: ", btn_path)
            return render_template("result.html", size=size, colname=colname, head=head,
                    describe=describe, corr=corr, isnull=isnull, btn_path=btn_path, res_code=res_code)
        except:
            return render_template("index.html", error="ファイルを読み込めませんでした")
    else:
        return redirect(url_for("index"))

@app.route("/result/hist", methods=["POST", "GET"])
def show_hist():
    global hist_url
    global scatter_url
    if request.method == "POST":
        try:
            col = request.form.get("hist-col")
            print("選択されたコラム名", col)
            hist_url = createHist(col)
            print("ヒストグラムのパス", hist_url)
            size, colname, head, describe, corr, isnull, btn_path, res_code = getResult()
            return render_template("result.html", size=size, colname=colname, head=head,
                    describe=describe, corr=corr, isnull=isnull, btn_path=btn_path,
                    res_code=res_code, hist_url=hist_url, scatter_url=scatter_url)
        except:
            return render_template("index.html", error="エラーが発生しました")
    return redirect(url_for('index'))

@app.route("/result/scatter", methods=["POST", "GET"])
def show_scatter():
    global scatter_url
    global hist_url
    if request.method == "POST":
        try:
            xcol = request.form.get("scatter-xcol")
            ycol = request.form.get("scatter-ycol")
            print("X軸 -> ", xcol)
            print("Y軸 -> ", ycol)
            scatter_url = createScatter(xcol, ycol)
            print("散布図のパス -> ", scatter_url)
            size, colname, head, describe, corr, isnull, btn_path, res_code = getResult()
            return render_template("result.html", size=size, colname=colname, head=head,
                    describe=describe, corr=corr, isnull=isnull, btn_path=btn_path,
                    res_code=res_code, hist_url=hist_url, scatter_url=scatter_url)
        except:
            return render_template("index.html", error="エラーが発生しました")
    return redirect(url_for('index'))
