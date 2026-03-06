from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "static" / "premium"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = A4
FONT_NAME = "IPAexGothic"


def register_japanese_font():
    font_path = BASE_DIR / "snippets" / "static" / "fonts" / "ipaexg.ttf"
    if not font_path.exists():
        raise FileNotFoundError(f"Font not found: {font_path}")
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(font_path)))


def draw_wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: int,
    y: int,
    max_chars: int = 48,
    line_height: int = 16,
):
    """超シンプルな折り返し"""
    lines = []
    for raw in text.split("\n"):
        s = raw.strip("\r")
        if not s:
            lines.append("")
            continue
        while len(s) > max_chars:
            lines.append(s[:max_chars])
            s = s[max_chars:]
        lines.append(s)

    for line in lines:
        c.drawString(x, y, line)
        y -= line_height
        if y < 60:
            c.showPage()
            c.setFont(FONT_NAME, 12)
            y = H - 72
    return y


def make_pdf(filename: str, title: str, subtitle: str, days: list[tuple[str, str]], footer: str):
    path = OUT_DIR / filename
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle(title)

    c.setFont(FONT_NAME, 18)
    c.drawString(48, H - 64, title)

    c.setFont(FONT_NAME, 12)
    c.drawString(48, H - 90, subtitle)

    y = H - 130
    c.setFont(FONT_NAME, 13)
    c.drawString(48, y, "7日ロードマップ")
    y -= 22

    c.setFont(FONT_NAME, 12)
    for day, body in days:
        c.setFont(FONT_NAME, 12)
        c.drawString(48, y, day)
        y -= 16
        c.setFont(FONT_NAME, 12)
        y = draw_wrapped_text(c, body, 64, y, max_chars=54, line_height=16)
        y -= 10

    y -= 10
    c.setFont(FONT_NAME, 10)
    y = draw_wrapped_text(c, footer, 48, y, max_chars=72, line_height=14)

    c.showPage()
    c.save()
    print(f"✅ wrote: {path}")


def main():
    register_japanese_font()

    make_pdf(
        "influence_7day_roadmap.pdf",
        "7日ロードマップ（影響力型）",
        "発信の型を作って、収益化までの距離を一気に縮める7日。",
        [
            ("Day1：テーマを1つに絞る", "過去に一番反応があった話題を3つ書き出し、共通点から「主テーマ」を1つ決める。"),
            ("Day2：伸びる型をパクる", "同ジャンル上位10投稿を保存→冒頭1行/構成/締めを分解してテンプレ化する。"),
            ("Day3：自己紹介固定文を作る", "「誰に」「何を」「どう変える」を100〜150字で作成。プロフィールにも反映。"),
            ("Day4：3本下書きする", "テンプレを使い、保存→下書き→予約（または当日投稿）まで完了。"),
            ("Day5：導線を置く", "無料プレゼント/診断/メルマガなど“次の一歩”を1つ決めてリンクを設置。"),
            ("Day6：反応が出る改善", "保存数・コメントの多かった要素を1つ増やし、伸びた投稿の続編を作る。"),
            ("Day7：週次運用に落とす", "毎週の投稿本数/作業時間/テーマを固定し、継続できる最小運用にする。"),
        ],
        "※ゴール：7日後に「テーマ・投稿テンプレ・導線・週次運用」が揃い、伸ばしながら収益化へ進める状態。"
    )

    make_pdf(
        "attack_7day_roadmap.pdf",
        "7日ロードマップ（攻撃型）",
        "回転で勝つ。リサーチ→出品/提案→改善を7日で習慣化。",
        [
            ("Day1：売れてる証拠を集める", "売れている商品/案件を30個集め、価格・特徴・売り文句を1行でメモ。"),
            ("Day2：勝ち筋を1つ決める", "30個から「自分が回せる」ジャンルを1つ選び、やらないことも決める。"),
            ("Day3：1ページで出せる形にする", "出品/提案/LPなど“1画面で完結する形”でまず公開できる状態にする。"),
            ("Day4：10件打つ", "出品/提案/営業を合計10件。質より回数、テンプレでOK。"),
            ("Day5：反応を分析する", "クリック/返信/購入の差を見て、タイトル・画像・冒頭文のどれが効いたか仮説を立てる。"),
            ("Day6：改善してもう10件", "仮説に沿って1点だけ改善→再び10件打つ。"),
            ("Day7：毎日回せる仕組みにする", "テンプレ・チェックリストを作り、毎日30分で回せる運用に固定。"),
        ],
        "※ゴール：7日後に「回転→改善」が回り始め、初収益/初返信に最短で近づく状態。"
    )

    make_pdf(
        "build_7day_roadmap.pdf",
        "7日ロードマップ（構築型）",
        "“完成させる構造”を作る。1画面ツールを7日で公開。",
        [
            ("Day1：悩みを1つに絞る", "対象者を1人に決め、悩み→理想→入力→出力を1枚のメモにする。"),
            ("Day2：最小機能を定義", "入力2つ・出力1つまでに削る（“便利”は全部捨てる）。"),
            ("Day3：画面を作る", "フォーム＋結果表示だけ作成。デザインは後回し。"),
            ("Day4：ロジックを入れる", "判定/生成のコアだけ実装。まず動けばOK。"),
            ("Day5：公開する", "本番にデプロイ。URLを取得して自分で1回使う。"),
            ("Day6：1人に使わせる", "友人/フォロワーに1人だけ依頼して、改善点を3つ回収。"),
            ("Day7：導線を置く", "トップ→診断→結果→Premiumの導線を整え、次に伸ばすポイントを決める。"),
        ],
        "※ゴール：7日後に「動くURL」と「改善の次アクション」が揃い、“作って止まる”を脱出した状態。"
    )


if __name__ == "__main__":
    main()