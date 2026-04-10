import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// 人格类型分析数据
const personalityAnalysis = {
  "ISTJ": {
    name: "物流师型",
    description: "ISTJ 型的人是严肃的、有责任心的和通情达理的社会坚定分子。他们值得信赖，他们重视承诺，对他们来说，言语就是庄严的誓言。",
    traits: [
      "实际、现实、脚踏实地",
      "注重事实和细节",
      "逻辑思维，有条理",
      "责任心强，可靠",
      "传统，尊重权威"
    ]
  },
  "ISFJ": {
    name: "守卫者型",
    description: "ISFJ 型的人忠诚、有奉献精神和同情心，理解别人的感受。他们意志清醒而有责任心，乐于为人所需。",
    traits: [
      "富有同情心，善良",
      "注重和谐与合作",
      "细致，注重细节",
      "忠诚，可靠",
      "传统，重视家庭"
    ]
  },
  "INFJ": {
    name: "提倡者型",
    description: "INFJ 型的人生活在思想的世界里。他们是独立的、有独创性的思想家，具有强烈的感情、坚定的原则和正直的人性。",
    traits: [
      "富有洞察力，有远见",
      "理想主义，有价值观",
      "富有同情心，关心他人",
      "创造力强，有独创性",
      "坚定，有原则"
    ]
  },
  "INTJ": {
    name: "建筑师型",
    description: "INTJ 型的人是完美主义者。他们强烈地要求个人自由和能力，同时在他们独创的思想中，不可动摇的信仰促使他们达到目标。",
    traits: [
      "逻辑思维，分析能力强",
      "有战略眼光，善于规划",
      "独立，自主",
      "高标准，完美主义",
      "创新，有洞察力"
    ]
  },
  "ISTP": {
    name: "鉴赏家型",
    description: "ISTP 型的人坦率、诚实、讲求实效，他们喜欢行动而非漫谈。他们很谦逊，对于完成工作的方法有很好的理解力。",
    traits: [
      "实际，动手能力强",
      "灵活，适应性强",
      "冷静，理性",
      "喜欢挑战，冒险",
      "注重效率，实用主义"
    ]
  },
  "ISFP": {
    name: "探险家型",
    description: "ISFP 型的人平和、敏感，他们保持着许多强烈的个人理想和自己的价值观念。他们更多地是通过行为而不是言辞表达自己深沉的情感。",
    traits: [
      "敏感，注重感受",
      "富有艺术细胞，创造力强",
      "灵活，适应性强",
      "温和，友好",
      "注重个人价值观"
    ]
  },
  "INFP": {
    name: "调停者型",
    description: "INFP 型的人珍视内在和谐胜过一切。他们敏感、理想化、忠诚，对于个人价值具有一种强烈的荣誉感。",
    traits: [
      "理想主义，价值观强",
      "富有同情心，关心他人",
      "创造力强，有想象力",
      "灵活，适应性强",
      "注重个人成长"
    ]
  },
  "INTP": {
    name: "逻辑学家型",
    description: "INTP 型的人是理性主义者和怀疑论者，他们善于思考，喜欢分析，对自己和他人都很苛求。",
    traits: [
      "逻辑思维，分析能力强",
      "好奇心强，喜欢探索",
      "独立，自主",
      "创意，有独创性",
      "理性，客观"
    ]
  },
  "ESTP": {
    name: "企业家型",
    description: "ESTP 型的人不会焦虑，因为他们是快乐的。ESTP 型的人活跃、随遇而安、天真率直。他们乐于享受现在的一切而不是为将来计划。",
    traits: [
      "精力充沛，活跃",
      "实际，注重结果",
      "灵活，适应性强",
      "善于社交，外向",
      "喜欢挑战，冒险"
    ]
  },
  "ESFP": {
    name: "表演者型",
    description: "ESFP 型的人乐意与人相处，有一种真正的生活热情。他们顽皮活泼，通过真诚和玩笑使别人感到事情更加有趣。",
    traits: [
      "外向，善于社交",
      "活泼，充满热情",
      "实际，注重当下",
      "灵活，适应性强",
      "善于表达，有表演天赋"
    ]
  },
  "ENFP": {
    name: "竞选者型",
    description: "ENFP 型的人充满热情和新思想。他们乐观、自然、富有创造性和自信，具有独创性的思想和对可能性的强烈感受。",
    traits: [
      "热情，充满活力",
      "创造力强，有想象力",
      "善于社交，外向",
      "理想主义，价值观强",
      "灵活，适应性强"
    ]
  },
  "ENTP": {
    name: "辩论家型",
    description: "ENTP 型的人喜欢兴奋与挑战。他们热情开放、足智多谋、健谈而聪明，擅长于许多事情，不断追求增加能力和个人权力。",
    traits: [
      "聪明，机智",
      "好奇心强，喜欢探索",
      "善于辩论，有说服力",
      "灵活，适应性强",
      "创新，有独创性"
    ]
  },
  "ESTJ": {
    name: "执行官型",
    description: "ESTJ 型的人高效率地工作，自我负责，监督他人工作，合理分配和处置资源，主次分明，井井有条；能制定和遵守规则，多喜欢在制度健全、等级分明、比较稳定的企业工作；倾向于选择较为务实的业务，以有形产品为主；喜欢工作中带有和人接触、交流的成分，但不以态度取胜；不特别强调工作的行业或兴趣，多以职业角度看待每一份工作。",
    traits: [
      "实际，注重结果",
      "善于组织和管理",
      "责任心强，可靠",
      "传统，尊重权威",
      "直接，果断"
    ]
  },
  "ESFJ": {
    name: "领事型",
    description: "ESFJ 型的人通过直接的行动和合作积极地以真实、实际的方法帮助别人。他们友好、富有同情心和责任感。",
    traits: [
      "友好，善于社交",
      "富有同情心，关心他人",
      "责任心强，可靠",
      "传统，重视家庭",
      "注重和谐与合作"
    ]
  },
  "ENFJ": {
    name: "主人公型",
    description: "ENFJ 型的人热爱人类，他们认为人的感情是最重要的。他们言辞温暖，善解人意，乐于助人。",
    traits: [
      "热情，富有感染力",
      "善于社交，外向",
      "富有同情心，关心他人",
      "理想主义，价值观强",
      "善于领导，有组织能力"
    ]
  },
  "ENTJ": {
    name: "指挥官型",
    description: "ENTJ 型的人是伟大的领导者和决策人。他们能轻易地看出事物具有的可能性，很高兴指导别人，使他们的想象成为现实。",
    traits: [
      "自信，果断",
      "善于领导和组织",
      "战略思维，有远见",
      "逻辑思维，分析能力强",
      "目标导向，注重结果"
    ]
  }
};

const Result = () => {
  const navigate = useNavigate();
  const [result, setResult] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);

  useEffect(() => {
    // 从本地存储获取测试结果
    const storedResult = localStorage.getItem("sbtitest_result");
    if (storedResult) {
      const parsedResult = JSON.parse(storedResult);
      setResult(parsedResult);
      setAnalysis(personalityAnalysis[parsedResult.personalityType] || null);
    } else {
      // 如果没有测试结果，重定向到首页
      navigate("/");
    }
  }, [navigate]);

  // 处理分享功能
  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `我的 SBTI 人格测试结果：${result?.personalityType} - ${analysis?.name}`,
        text: analysis?.description,
        url: window.location.href
      }).catch((error) => console.error("分享失败:", error));
    } else {
      // 复制链接到剪贴板
      navigator.clipboard.writeText(window.location.href).then(() => {
        alert("链接已复制到剪贴板");
      }).catch((error) => console.error("复制失败:", error));
    }
  };

  // 重新测试
  const handleRetakeTest = () => {
    // 清除本地存储的结果
    localStorage.removeItem("sbtitest_result");
    // 跳转到测试页面
    navigate("/test");
  };

  if (!result || !analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-gray-600">正在加载结果...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        {/* 结果卡片 */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <h1 className="text-3xl font-bold text-center text-gray-900 mb-2">
            你的 SBTI 人格类型
          </h1>
          <div className="flex justify-center mb-6">
            <div className="bg-purple-100 rounded-full p-4 inline-block">
              <span className="text-4xl font-bold text-purple-600">
                {result.personalityType}
              </span>
            </div>
          </div>
          <h2 className="text-xl font-semibold text-center text-gray-800 mb-4">
            {analysis.name}
          </h2>
          <p className="text-gray-600 text-center mb-6">
            {analysis.description}
          </p>

          {/* 人格特点 */}
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-800 mb-3">
              你的人格特点
            </h3>
            <ul className="space-y-2">
              {analysis.traits.map((trait: string, index: number) => (
                <li key={index} className="flex items-center">
                  <div className="w-2 h-2 bg-purple-600 rounded-full mr-3"></div>
                  <span className="text-gray-700">{trait}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 测试完成时间 */}
          <div className="text-sm text-gray-500 text-center mb-6">
            测试完成时间：{new Date(result.completedAt).toLocaleString()}
          </div>

          {/* 操作按钮 */}
          <div className="flex flex-col space-y-3">
            <button
              className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all"
              onClick={handleShare}
            >
              分享结果
            </button>
            <button
              className="w-full py-3 bg-white text-purple-600 border border-purple-600 rounded-lg hover:bg-purple-50 transition-all"
              onClick={handleRetakeTest}
            >
              重新测试
            </button>
            <button
              className="w-full py-3 bg-white text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
              onClick={() => navigate("/")}
            >
              返回首页
            </button>
          </div>
        </div>

        {/* 提示信息 */}
        <div className="bg-purple-50 rounded-lg p-4 mb-8">
          <p className="text-sm text-purple-700">
            提示：SBTI 人格测试结果仅供参考，不能完全定义你的人格。每个人都是独特的，测试结果只是帮助你更好地了解自己的一个工具。
          </p>
        </div>
      </div>
    </div>
  );
};

export default Result;