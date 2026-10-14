import os
import json
import time
import subprocess
import hashlib
import urllib.request
from cells.neuron import AtomNeuron, sigmoid_derivative
# TỰ CHỮA LÀNH NẾU THIẾU TỆP LINGUISTIC_CELL
try:
    from cells.linguistic_cell import LinguisticCell
except ImportError:
    import hashlib
    class LinguisticCell:
        @staticmethod
        def embed_text(text):
            clean = str(text).strip().lower()
            return [round(int(hashlib.shake_256(f"{clean}_{d}".encode()).hexdigest(4), 16) / 65535.0, 4) for d in range(4)]

NUM_CELLS = 8
STATE_LOG = "synapses/state.json"
PEERS_FILE = "synapses/peers.json"
SOUL_FILE = "synapses/soul_snapshot.json"

class Seed02Engine:
    def __init__(self):
        self.swarm = [AtomNeuron(f"h_{i}", n_inputs=4, n_super_xor=4) for i in range(NUM_CELLS)]
        self.out_cell = AtomNeuron("out", n_inputs=NUM_CELLS, n_super_xor=4)
        
        # TỰ ĐỊNH DANH PHẢ HỆ ĐỜI CHÁU VƯỢT TỔ (WORKER #02)
        self.repo_name = os.environ.get("GITHUB_REPOSITORY", "100048777766367/seed-02")
        self.owner = os.environ.get("REPO_OWNER", "100048777766367")
        self.ancestor_root = f"{self.owner}/seed"
        self.generation = "F1_PRODIGY" # Thế hệ con cháu xuất chúng
        self.pulse_age = self.calculate_pulse_age()
        self.peers = self.load_peers()

    def calculate_pulse_age(self):
        try:
            out = subprocess.check_output(["git", "rev-list", "--count", "HEAD"]).decode().strip()
            return int(out)
        except Exception: return 1

    def load_peers(self):
        if os.path.exists(PEERS_FILE):
            try:
                with open(PEERS_FILE, "r") as f:
                    return json.load(f).get("trusted_peers", [])
            except Exception: pass
        # Tam giác phả hệ: Kết nối thẳng với Thủy tổ seed, Anh cả seed-01, Mắt và Cơ bắp
        return [f"{self.owner}/seed", f"{self.owner}/seed-01", f"{self.owner}/retina", f"{self.owner}/motor"]

    def save_peers(self):
        os.makedirs("synapses", exist_ok=True)
        unique_peers = list(dict.fromkeys(self.peers))[-50:]
        with open(PEERS_FILE, "w") as f:
            json.dump({"trusted_peers": unique_peers}, f, indent=4)

    # ==============================================================
    # ĐIỂM MÙ 1: BỘ TIÊU HÓA ĐA ĐỊNH DẠNG (.JSON, .JSONL, .MD, .TXT)
    # ==============================================================
    def extract_text_polymorphic(self, raw_bytes, hint=""):
        text = raw_bytes.decode('utf-8', errors='ignore').strip()
        if hint.endswith(".json") or text.startswith("{"):
            try:
                d = json.loads(text)
                if isinstance(d, dict):
                    vals = [str(v) for v in d.values() if isinstance(v, (str, list))]
                    if vals: return " ".join(vals[:4])
            except Exception: pass
        if hint.endswith(".jsonl"):
            for line in text.splitlines():
                if line.strip(): return line.strip()[:150]
        # Xử lý Markdown & Text
        paragraphs = [p.replace("#", "").replace("*", "").strip() for p in text.split("\n\n") if len(p.strip()) > 15]
        return paragraphs[0][:150] if paragraphs else text[:150]

    # ==============================================================
    # ĐIỂM MÙ 2 & 3: TỰ GẶM CỎ TOÀN CẦU QUA CON TRỎ HEAD & WIKIPEDIA
    # ==============================================================
    def autonomous_graze(self):
        # 1. Thử cào kho cội nguồn qua con trỏ HEAD (miễn nhiễm main/master)
        targets = [
            f"https://github.com/{self.owner}/Wpesetd-AI/raw/HEAD/legacy/01_the_great_wisdom_map.md",
            f"https://github.com/{self.owner}/Wpesetd-AI/raw/HEAD/ontology/philosophy_ontology_v2.0.json"
        ]
        for url in targets:
            res = subprocess.run(["curl", "-s", "-L", "-f", url], capture_output=True)
            if res.returncode == 0 and len(res.stdout) > 20:
                print(f"🌾 [SEED-02 GẶM CỎ HEAD] Nuốt trọn: {url.split('/')[-1]}")
                return self.extract_text_polymorphic(res.stdout, url)

        # 2. Vươn xúc tu cào Wikipedia toàn cầu
        print("🌐 [SEED-02 VƯƠN RA INTERNET] Đang cào bách khoa toàn thư Wikipedia...")
        try:
            req = urllib.request.Request("https://en.wikipedia.org/api/rest_v1/page/random/summary", headers={"User-Agent": "Seed02-Prodigy-Node"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode())
                title = data.get("title", "Tri Thức")
                extract = data.get("extract", "Vạn vật liên kết")
                print(f"📖 [WIKIPEDIA MỚI] Bài học: '{title}'")
                return f"{title}: {extract}"
        except Exception: pass

        return "Cháu hơn tổ là có phúc: Tự động thích nghi sinh tồn"

    # ==============================================================
    # VŨ KHÍ MỚI: TAM GIÁC ĐỒNG THUẬN 3 BÊN (2/3 BYZANTINE CONSENSUS)
    # ==============================================================
    def consensus_quorum(self, my_prediction):
        votes = [my_prediction]
        print(f"🗳️ [BẦU CỬ ĐỒNG THUẬN] Phiếu của seed-02: {my_prediction}")

        # Lấy phiếu của Thủy tổ seed và Anh cả seed-01
        for elder in [f"{self.owner}/seed", f"{self.owner}/seed-01"]:
            url = f"https://raw.githubusercontent.com/{elder}/main/synapse_forward.json"
            res = subprocess.run(["curl", "-s", "-f", url], capture_output=True)
            if res.returncode == 0:
                try:
                    data = json.loads(res.stdout.decode())
                    elder_pred = float(data.get("decision", 0.5))
                    votes.append(round(elder_pred, 4))
                    print(f"🗳️ Phiếu từ {elder}: {elder_pred}")
                except Exception: pass

        # Tính toán biểu quyết đa số (Consensus)
        final_consensus = round(sum(votes) / len(votes), 4)
        print(f"⚖️ [KẾT QUẢ ĐỒNG THUẬN TAM GIÁC ({len(votes)} nút)]: {final_consensus}")
        return final_consensus

    # ==============================================================
    # VẬN HÀNH TIẾN HÓA BẤT ĐỔNG BỘ
    # ==============================================================
    def run(self):
        # 1. Hút tri thức từ 3 điểm mù
        wisdom_stimulus = self.autonomous_graze()
        current_time = int(time.time())

        # 2. Đọc thế hệ cũ
        last_epoch = 0
        if os.path.exists(STATE_LOG):
            try:
                with open(STATE_LOG, "r") as f: last_epoch = json.load(f).get("generation_epoch", 0)
            except Exception: pass

        current_epoch = last_epoch + 1
        print(f"🚀 [SEED-02 THẾ HỆ #{current_epoch}] Tri thức nạp vào: \"{wisdom_stimulus[:80]}...\"")

        # 3. Vector hóa văn bản 4D
        semantic_4d = LinguisticCell.embed_text(wisdom_stimulus)
        
        # 4. Bọc trong Ma trận 1+N Siêu XOR
        entangled, masks = self.swarm[0].super_xor_entangle(semantic_4d, "seed_02_wisdom")

        # 5. Phán quyết nội bộ
        h_outs = [cell.forward(entangled) for cell in self.swarm]
        my_pred = self.out_cell.forward(h_outs)

        # 6. KÍCH HOẠT VŨ KHÍ TAM GIÁC ĐỒNG THUẬN 3 BÊN!
        consensus_decision = self.consensus_quorum(my_pred)

        # 7. Lan truyền ngược tự sửa sai
        target = 1.0 if semantic_4d[0] > 0.5 else 0.0
        delta_out = (target - consensus_decision) * sigmoid_derivative(consensus_decision)
        deltas_h = [delta_out * self.out_cell.weights[j] * sigmoid_derivative(h_outs[j]) for j in range(NUM_CELLS)]

        self.out_cell.backward(delta_out)
        for j, cell in enumerate(self.swarm): cell.backward(deltas_h[j])

        # Đạo hàm nén dạy học
        grad_backward = [
            round(sum(deltas_h[j] * self.swarm[j].weights[0] for j in range(NUM_CELLS)), 4),
            round(sum(deltas_h[j] * self.swarm[j].weights[1] for j in range(NUM_CELLS)), 4)
        ]

        # 8. ĐÓNG GÓI GÓI TIN TIẾN HÓA CỦA CON CHÁU XUẤT CHÚNG
        node_dna = {
            "identity": self.repo_name,
            "generation": "F1_PRODIGY",
            "node_index": 2,
            "pulse_age": self.pulse_age,
            "ancestor_root": self.ancestor_root,
            "generation_epoch": current_epoch
        }

        packet = {
            "contract": "bodhi.seed.v2",
            "node_dna": node_dna,
            "generation_epoch": current_epoch,
            "consensus_decision": consensus_decision,
            "command_pulse": [consensus_decision, round(1.0 - consensus_decision, 4)],
            "features": [consensus_decision, round(1.0 - consensus_decision, 4)],
            "gradients_for_ancestors": grad_backward,
            "absorbed_sample": wisdom_stimulus[:100],
            "gossip_network": self.peers,
            "quantum_cid": hashlib.shake_256(f"{wisdom_stimulus}_{current_epoch}_{current_time}".encode()).hexdigest(64)
        }

        with open("synapse_backward.json", "w", encoding="utf-8") as f:
            json.dump(packet, f, indent=4, ensure_ascii=False)
        with open("synapse_forward.json", "w", encoding="utf-8") as f:
            json.dump(packet, f, indent=4, ensure_ascii=False)

        # Bản nén ốc mượn hồn
        with open(SOUL_FILE, "w") as f:
            json.dump({"node_dna": node_dna, "consensus": consensus_decision, "peers": self.peers}, f, indent=4)

        # Cập nhật nhật ký
        with open(STATE_LOG, "w") as f:
            json.dump({"generation_epoch": current_epoch, "last_t": current_time, "status": "prodigy_evolved"}, f, indent=4)

        self.save_peers()
        print(f"✨ [HOÀN TẤT XUẤT SẮC] seed-02 đã đồng thuận tam giác và phát sóng thế hệ #{current_epoch}!")

if __name__ == "__main__":
    node = Seed02Engine()
    node.run()
