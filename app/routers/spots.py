"""景点资源接口"""

from fastapi import APIRouter, Request, Query

from app.schemas.common import ok, err, Pagination

router = APIRouter(tags=["Spots"])

# 灵山 16 景点 seed 数据
_SEED_SPOTS = [
    {"id": "LS-001", "scenicId": "SA-001", "name": "灵山大佛", "nameEn": "Lingshan Giant Buddha", "tags": ["佛教文化", "标志性建筑", "必游"], "location": "景区中轴线北端", "summary": "高 88 米的青铜释迦牟尼立像，灵山胜境核心标志", "intro": "灵山大佛高 88 米，加上基座总高达 101.5 米...", "highlights": ["抱佛脚祈福", "登高望远"], "source": "public_demo_package", "freshnessLevel": "high"},
    {"id": "LS-002", "scenicId": "SA-001", "name": "灵山梵宫", "nameEn": "Lingshan Brahma Palace", "tags": ["建筑艺术", "佛教文化", "必游"], "location": "大佛广场东侧", "summary": "融合中国传统与佛教艺术的宏伟宫殿", "intro": "梵宫是灵山胜境的核心建筑之一，以华藏世界为设计理念...", "highlights": ["华藏世界大殿", "琉璃艺术墙"], "source": "public_demo_package", "freshnessLevel": "high"},
    {"id": "LS-003", "scenicId": "SA-001", "name": "九龙灌浴", "nameEn": "Nine Dragons Bathing", "tags": ["表演", "标志性景观", "必游"], "location": "景区入口中轴线", "summary": "大型音乐喷泉，再现释迦牟尼诞生场景", "intro": "九龙灌浴是灵山胜境的标志性景观之一...", "highlights": ["喷泉表演", "太子佛像出浴"], "source": "public_demo_package", "freshnessLevel": "high"},
    {"id": "LS-004", "scenicId": "SA-001", "name": "五印坛城", "nameEn": "Five Mudra Mandala", "tags": ["藏传佛教", "建筑", "文化"], "location": "梵宫东北侧", "summary": "藏传佛教风格建筑，展示藏文化魅力", "intro": "五印坛城是一座藏传佛教风格的建筑...", "highlights": ["坛城建筑群", "藏文化展览"], "source": "public_demo_package", "freshnessLevel": "high"},
    {"id": "LS-005", "scenicId": "SA-001", "name": "祥符禅寺", "nameEn": "Xiangfu Temple", "tags": ["历史", "禅宗", "古寺"], "location": "大佛脚下南侧", "summary": "千年古寺，灵山佛教文化的起点", "intro": "祥符禅寺始建于唐代，是灵山地区最早的佛教寺院...", "highlights": ["古寺建筑", "钟楼"], "source": "public_demo_package", "freshnessLevel": "high"},
    {"id": "LS-006", "scenicId": "SA-001", "name": "阿育王柱", "nameEn": "Ashoka Pillar", "tags": ["历史遗迹", "石刻"], "location": "景区入口广场", "summary": "印度阿育王时代的石柱风格遗迹", "intro": "阿育王柱是仿印度阿育王时代的石柱...", "highlights": ["石柱雕刻", "经文"], "source": "public_demo_package", "freshnessLevel": "medium"},
    {"id": "LS-007", "scenicId": "SA-001", "name": "降魔浮雕", "nameEn": "Demon-Subduing Relief", "tags": ["浮雕", "佛教故事"], "location": "大佛基座周围", "summary": "讲述释迦牟尼悟道降魔的大型浮雕", "intro": "降魔浮雕以生动的画面展现了佛陀降魔成道的故事...", "highlights": ["浮雕艺术", "佛教故事"], "source": "public_demo_package", "freshnessLevel": "medium"},
    {"id": "LS-008", "scenicId": "SA-001", "name": "百子戏弥勒", "nameEn": "Maitreya with Children", "tags": ["雕塑", "弥勒"], "location": "南门附近", "summary": "弥勒菩萨与百名童子的欢乐雕塑群", "intro": "百子戏弥勒是一座大型铜雕...", "highlights": ["铜雕群像", "互动拍照"], "source": "public_demo_package", "freshnessLevel": "medium"},
    {"id": "LS-009", "scenicId": "SA-001", "name": "天下第一掌", "nameEn": "Giant Hand of Buddha", "tags": ["雕塑", "互动"], "location": "大佛广场", "summary": "灵山大佛右手 1:1 复制铜像", "intro": "天下第一掌是灵山大佛右手的等比例复制品...", "highlights": ["摸手祈福", "铜像工艺"], "source": "public_demo_package", "freshnessLevel": "medium"},
    {"id": "LS-010", "scenicId": "SA-001", "name": "曼飞龙塔", "nameEn": "Manfeilong Pagoda", "tags": ["佛塔", "建筑"], "location": "景区西侧", "summary": "仿云南傣族风格的白塔群", "intro": "曼飞龙塔是仿照云南西双版纳曼飞龙白塔建造...", "highlights": ["白塔群", "民族风情"], "source": "public_demo_package", "freshnessLevel": "medium"},
    {"id": "LS-011", "scenicId": "SA-001", "name": "香水海", "nameEn": "Perfume Sea", "tags": ["水景", "休闲"], "location": "梵宫前广场", "summary": "梵宫前的大型水景广场", "intro": "香水海是梵宫前的大型水景...", "highlights": ["水景倒影", "夜景灯光"], "source": "public_demo_package", "freshnessLevel": "medium"},
    {"id": "LS-012", "scenicId": "SA-001", "name": "灵山胜境博物馆", "nameEn": "Lingshan Museum", "tags": ["博物馆", "展览"], "location": "景区南侧服务中心", "summary": "展示灵山佛教文化历史的博物馆", "intro": "博物馆收藏了大量佛教文物和灵山历史资料...", "highlights": ["文物展览", "历史文化"], "source": "public_demo_package", "freshnessLevel": "low"},
    {"id": "LS-013", "scenicId": "SA-001", "name": "菩提大道", "nameEn": "Bodhi Avenue", "tags": ["景观道", "休闲"], "location": "景区南门至大佛广场", "summary": "连接景区大门与大佛广场的主景观道", "intro": "菩提大道两侧种植银杏和菩提树...", "highlights": ["林荫大道", "石刻经文"], "source": "public_demo_package", "freshnessLevel": "medium"},
    {"id": "LS-014", "scenicId": "SA-001", "name": "转经廊", "nameEn": "Prayer Wheel Corridor", "tags": ["藏传佛教", "互动"], "location": "五印坛城旁", "summary": "藏式转经筒长廊", "intro": "转经廊共有 108 个转经筒...", "highlights": ["转经体验", "藏文化"], "source": "manual_seed", "freshnessLevel": "low"},
    {"id": "LS-015", "scenicId": "SA-001", "name": "灵山茶室", "nameEn": "Lingshan Tea House", "tags": ["餐饮", "休闲"], "location": "菩提大道中段", "summary": "景区内品茶休息的场所", "intro": "茶室提供灵山特色素茶和点心...", "highlights": ["品茶休憩", "素斋体验"], "source": "manual_seed", "freshnessLevel": "low"},
    {"id": "LS-016", "scenicId": "SA-001", "name": "佛足坛", "nameEn": "Buddha Foot Altar", "tags": ["佛教", "石刻"], "location": "祥符禅寺旁", "summary": "刻有佛陀足印的石坛", "intro": "佛足坛供奉着佛陀足印的石刻...", "highlights": ["足印石刻", "祈福仪式"], "source": "manual_seed", "freshnessLevel": "low"},
]

_SEED_GUIDES = {
    "LS-001": {"shortText": "灵山大佛", "briefText": "灵山大佛高88米，是世界上最高的青铜释迦牟尼立像，灵山胜境的核心标志。", "longText": "灵山大佛高88米，加上基座总高达101.5米。大佛采用青铜铸造，面容慈祥庄严。您可以登临大佛基座，近距离感受佛法的庄严与慈悲。在这里，您可以抱佛脚祈福，也可以远眺太湖美景。", "fallbackText": "灵山大佛是灵山胜境的标志，建议您前往大佛广场近距离观赏。"},
    "LS-002": {"shortText": "灵山梵宫", "briefText": "梵宫是融合中国传统与佛教艺术的宏伟宫殿，以华藏世界为设计理念。", "longText": "梵宫是灵山胜境的核心建筑之一，建筑面积达7万平方米。内部以华藏世界为设计理念，融合了敦煌壁画、琉璃艺术、木雕、石雕等多种艺术形式。大殿中央的华藏世界是整个梵宫的精华所在，金碧辉煌，令人叹为观止。", "fallbackText": "梵宫是灵山必游景点，建议您前往参观华藏世界大殿。"},
    "LS-003": {"shortText": "九龙灌浴", "briefText": "大型音乐喷泉表演，再现释迦牟尼诞生时九龙吐水的场景。", "longText": "九龙灌浴是灵山胜境的标志性景观之一。每天定时上演的大型音乐喷泉表演，九条金龙环绕莲座，随着音乐缓缓升起，再现释迦牟尼太子诞生时九龙吐水沐浴的庄严场景。表演时间：每日10:00、14:00、16:00。", "fallbackText": "九龙灌浴表演每日三场，分别为10点、14点和16点。"},
    "LS-004": {"shortText": "五印坛城", "briefText": "藏传佛教风格建筑群，展示藏族文化与佛教艺术的完美融合。", "longText": "五印坛城是一座典型的藏传佛教风格建筑，仿照西藏大昭寺而建。坛城内部展示了丰富的藏族文化元素，包括唐卡、酥油花、藏文经书等，让游客感受到浓郁的藏文化气息。", "fallbackText": "五印坛城展示了藏传佛教的独特魅力，值得一游。"},
    "LS-005": {"shortText": "祥符禅寺", "briefText": "千年古寺，灵山佛教文化的历史起点。", "longText": "祥符禅寺始建于唐代，距今已有千年历史。寺院虽然规模不大，但古朴幽静，是灵山地区最早的佛教寺院。寺内有钟楼、大雄宝殿等传统建筑，钟声悠远，让人心生宁静。", "fallbackText": "祥符禅寺位于大佛脚下南侧，是灵山历史最悠久的寺院。"},
}


@router.get("/spots")
def list_spots(
    keyword: str = Query(None),
    tag: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    request: Request = None,
):
    trace_id = request.state.trace_id
    spots = _SEED_SPOTS

    if tag:
        spots = [s for s in spots if tag in s["tags"]]
    if keyword:
        kw = keyword.lower()
        spots = [s for s in spots if kw in s["name"].lower() or kw in s["summary"].lower()]

    total = len(spots)
    page = offset // limit + 1
    paginated = spots[offset : offset + limit]
    total_pages = (total + limit - 1) // limit

    return ok(
        data={"items": paginated, "total": total},
        trace_id=trace_id,
        pagination=Pagination(page=page, limit=limit, total=total, totalPages=total_pages),
    )


@router.get("/spots/{spot_id}")
def get_spot(spot_id: str, request: Request):
    trace_id = request.state.trace_id
    for s in _SEED_SPOTS:
        if s["id"] == spot_id:
            return ok(data=s, trace_id=trace_id)
    return err("SPOT_NOT_FOUND", "NOT_FOUND", f"景点 {spot_id} 不存在", trace_id)


@router.get("/spots/{spot_id}/guide")
def get_spot_guide(spot_id: str, style: str = Query(None), duration: str = Query(None), request: Request = None):
    trace_id = request.state.trace_id
    guide = _SEED_GUIDES.get(spot_id)
    if not guide:
        return err("SPOT_NOT_FOUND", "NOT_FOUND", f"景点 {spot_id} 的讲解词不存在", trace_id)
    return ok(data={**guide, "spotId": spot_id, "source": "public_demo_package"}, trace_id=trace_id)
