let pyodide = null;
let fontLoaded = false;

const initPy = `
from fontTools.ttLib import TTFont
class Ttf:
	def __init__(self, font):
		self.status = 0
		try:
			self.font = TTFont(font)
			if not self.font:
				self.status = 1
			self.set_cmap(3, 10)
			if "GSUB" not in self.font:
				self.status = 1
			self.gsub = self.font["GSUB"].table
			self.build_map()
			if not self.mapping:
				self.status = 1
		except Exception:
			self.status = 1
	
	def set_cmap(self, p, e):
		tmp = self.font["cmap"].getcmap(p, e)
		if not tmp:
			return 1
		self.cmap = tmp.cmap
		return 0
		
	def rename(self, family, full, postscript):
		for rec in self.font["name"].names:
			# font family
			if rec.nameID == 1:
				rec.string = family.encode(rec.getEncoding())
			# font display
			if rec.nameID == 4:
				rec.string = full.encode(rec.getEncoding())
			# unique id
			if rec.nameID == 6:
				rec.string = postscript.replace(" ", "").encode(rec.getEncoding())
		return 0

	def save_font(self, path):
		try:
			self.font.save(path)
		except Exception:
			return 1
		return 0

	def build_map(self):
		self.mapping = {}
		for f in self.gsub.FeatureList.FeatureRecord:
			result = {}
			for idx in f.Feature.LookupListIndex:
				for sub in self.gsub.LookupList.Lookup[idx].SubTable:
					if hasattr(sub, "mapping"):
						result.update(sub.mapping)
			if result:
				self.mapping[f.FeatureTag] = result
	
	def list_map(self):
		log("tag: {cmap[codepoint]: cmap[codepoint.alt]}")
		for tag, f in self.mapping.items():
			print(f"{tag}: {f}")
	
	def restyle(self, cp, tag):
		if not isinstance(cp, int):
			cp = ord(cp)
		if cp not in self.cmap:
			return 2
		g = self.cmap[cp]
		if tag not in self.mapping:
			return 3
		if g not in self.mapping[tag]:
			return 4
		alt = self.mapping[tag][g]
		self.font["glyf"][g] = self.font["glyf"][alt]
		self.font["hmtx"][g] = self.font["hmtx"][alt]
		return 0
`

async function init() {
	show_message("ロード中です...", "info");
    if (!pyodide) {
        pyodide = await loadPyodide();
        await pyodide.loadPackage("micropip");
        const micropip = pyodide.pyimport("micropip");
        await micropip.install("fonttools");
        await pyodide.runPythonAsync(initPy);
    }

    document.getElementById('font').addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const buf = await file.arrayBuffer();
        pyodide.FS.writeFile("input.ttf", new Uint8Array(buf));
        await pyodide.runPythonAsync(`font = Ttf("input.ttf")`);
		const res = await pyodide.runPythonAsync(`font.status`);
		if (res > 0) show_message("非対応のファイルです。");
		else { show_message("ファイルが正常にロードされました。", "success"); fontLoaded = true; }
    });

	document.getElementById('overwrite').addEventListener('click', async (e) => {
		e.preventDefault();
		if (!fontLoaded) { show_message("フォントを選択してください"); return; }
		const cp = document.getElementById('codepoint').value;
		const tag = document.getElementById('tag').value;
		const lega = document.getElementById('legacy').checked;
		if (!cp || !tag) {
			show_message("文字とタグを指定してください。");
			return;
		}
		let res = await pyodide.runPythonAsync(`font.restyle("${cp}", "${tag}")`);
		if (lega && res > 0) {
			res += await pyodide.runPythonAsync(`font.set_cmap(3, 1)`);
			res += await pyodide.runPythonAsync(`font.restyle("${cp}", "${tag}")`);
			res += await pyodide.runPythonAsync(`font.set_cmap(3, 10)`);
		}
		if (res > 0) show_message("文字とタグの組合せがありません。");
		else {
			add_history(cp, tag);
			document.getElementById('codepoint').value = '';
			document.getElementById('tag').value = '';
			show_message("変換しました。", "success");
		}
	});

	document.getElementById('saveFont').addEventListener('click', async (e) => {
		e.preventDefault();
		if (!fontLoaded) { show_message("フォントを選択してください"); return; }
		const family = document.getElementById('font-family').value;
		const display = document.getElementById('font-display').value;
		const id = document.getElementById('font-id').value;
		if (!family || !display || !id) {
			show_message("名前をすべて入力してください。");
			return;
		}
		let res = await pyodide.runPythonAsync(`font.rename("${family}", "${display}", "${id}")`);
		if (res > 0) show_message("命名に失敗しました。");
		res = await pyodide.runPythonAsync(`font.save_font("${id}.ttf")`);
		if (res > 0) show_message("保存に失敗しました。");
		const data = pyodide.FS.readFile(id + ".ttf");
		const blob = new Blob([data], { type: "font/ttf" });

		const a = document.createElement("a");
		a.href = URL.createObjectURL(blob);
		a.download = id + ".ttf";
		a.click();
	});
	show_message("ロードが完了しました。", "success");
}

function show_message(val, type = "error") {
	const msg = document.getElementById('message');

	msg.textContent = val;
	msg.className = `show ${type}`;

	clearTimeout(msg.timer);
	msg.timer = setTimeout(() => {
		msg.className = "";
	}, 3000);
}

function add_history(cp, tag) {
	const ul = document.getElementById("history");
	const li = document.createElement("li");
	li.textContent = `[${cp}] ${tag}`;
	ul.prepend(li);
}

async function main() {
    await init();
}

main();
