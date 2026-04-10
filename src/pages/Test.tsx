import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// 测试问题数据
const questions = [
  "我更喜欢在安静的环境中工作。",
  "我喜欢尝试新的事物和体验。",
  "明天有个重要考试，但今天有个超好玩的聚会，你会：",
  "当你看到一个感人的电影场景时：",
  "我认为逻辑和理性比情感更重要。",
  "我经常会做一些冲动的决定。",
  "我喜欢制定详细的计划。",
  "我认为人的性格是可以改变的。",
  "我更喜欢和少数几个亲密的朋友相处，而不是一大群人。",
  "当朋友告诉你一个秘密时，你会：",
  "如果有机会和陌生人一起旅行，你会：",
  "我认为工作应该先于娱乐。",
  "我经常会反思自己的行为和想法。",
  "我更喜欢明确的规则和结构，而不是模糊的指导方针。",
  "当你遇到一个新认识的人时，你会：",
  "我认为诚实是最重要的品质之一。",
  "我经常会感到焦虑或担忧。",
  "我喜欢挑战传统观念。",
  "我认为团队合作比个人努力更重要。",
  "当你需要做决定时，你会：",
  "我更喜欢有规律的生活，而不是充满变化的生活。",
  "我经常会为别人着想。",
  "我喜欢学习新的知识和技能。",
  "当你犯了错误时，你会：",
  "我认为保持开放的心态很重要。"
];

// 选项数据
const options = [
  ["A 不认同", "B 中立", "C 认同"],
  ["A 不认同", "B 中立", "C 认同"],
  ["A 翘了！反正就一次！", "B 干脆请个假吧。", "C 都快考试了还去啥。"],
  ["A 我哭了。。", "B 这是什么。。", "C 这不是我！"],
  ["A 认同", "B 中立", "C 不认同"],
  ["A 并没有", "B 也许？", "C 是的！（问心无愧骄傲脸）"],
  ["A 然而计划不如变化快。", "B 有时能完成，有时不能。", "C 我讨厌被打破计划。"],
  ["A 是这样的。", "B 也许是，也许不是。", "C 这简直是胡扯"],
  ["A 认同", "B 中立", "C 不认同"],
  ["A 拉稀不可能5小时，也许ta隐瞒了我。", "B 在信任和怀疑之间摇摆。", "C 也许今天ta真的不太舒服。"],
  ["A 那很爽了", "B 都行无所谓", "C 我更喜欢保留独立空间"],
  ["A 我被逼到最后确实执行力超强。。。", "B 啊，有时候吧。", "C 是的，事情本来就该被推进"],
  ["A 不认同", "B 中立", "C 认同"],
  ["A 对\"朋友的朋友\"天然有点距离感，怕影响二人关系", "B 看对方，能玩就玩。", "C 朋友的朋友应该也算我的朋友！要热情聊天"],
  ["A 不认同", "B 中立", "C 认同"],
  ["A 呜呜她真好真可爱！居然给我棒棒糖！", "B 一脸懵逼，作挠头状", "C 这也许是一种新型诈骗？还是走开为好。"],
  ["A 反复思考后感觉应该选A？", "B 啊，要不选B？", "C 不会就选C？"],
  ["A 吃喝拉撒", "B 艺术爱好", "C 饮酒", "D 健身"],
  ["A 再坐三十分钟看看，说不定就有了。", "B 用力拍打自己的屁股并说：\"死屁股，快拉啊！\"", "C 使用开塞露，快点拉出来才好。"],
  ["A 不认同", "B 中立", "C 认同"],
  ["A 确实", "B 有时", "C 不是"],
  ["A 不认同", "B 中立", "C 认同"],
  ["A 不认同", "B 中立", "C 认同"],
  ["A 我更喜欢依赖与被依赖", "B 看情况", "C 是的！（斩钉截铁地说道）"],
  ["A 不认同", "B 中立", "C 认同"]
];

const Test = () => {
  const navigate = useNavigate();
  const [answers, setAnswers] = useState<number[]>(new Array(questions.length).fill(-1));
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [progress, setProgress] = useState(0);

  // 计算进度
  useEffect(() => {
    const answeredCount = answers.filter(answer => answer !== -1).length;
    const newProgress = (answeredCount / questions.length) * 100;
    setProgress(newProgress);
  }, [answers]);

  // 处理选项选择
  const handleOptionSelect = (optionIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = optionIndex;
    setAnswers(newAnswers);

    // 自动跳转到下一题
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  // 处理提交测试
  const handleSubmit = () => {
    // 检查是否所有问题都已回答
    if (answers.some(answer => answer === -1)) {
      alert("请回答所有问题");
      return;
    }

    // 计算人格类型
    const calculatePersonalityType = () => {
      // 这里简化了计算逻辑，实际应该根据具体的评分标准计算
      const types = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"];
      return types[Math.floor(Math.random() * types.length)];
    };

    const personalityType = calculatePersonalityType();

    // 存储结果到本地存储
    localStorage.setItem("sbtitest_result", JSON.stringify({
      personalityType,
      answers,
      completedAt: new Date().toISOString()
    }));

    // 跳转到结果页面
    navigate("/result");
  };

  // 处理上一题
  const handlePrevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  // 处理下一题
  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        {/* 进度条 */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-600">进度</span>
            <span className="text-sm font-medium text-purple-600">{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-purple-600 transition-all duration-300 ease-in-out" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* 问题卡片 */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            问题 {currentQuestion + 1}/{questions.length}
          </h2>
          <p className="text-xl font-medium text-gray-800 mb-6">
            {questions[currentQuestion]}
          </p>

          {/* 选项 */}
          <div className="space-y-3">
            {options[currentQuestion].map((option, index) => (
              <button
                key={index}
                className={`w-full text-left p-4 rounded-lg border transition-all ${answers[currentQuestion] === index 
                  ? 'border-purple-600 bg-purple-50 text-purple-700' 
                  : 'border-gray-200 hover:border-purple-300 hover:bg-purple-50'}`}
                onClick={() => handleOptionSelect(index)}
              >
                {option}
              </button>
            ))}
          </div>
        </div>

        {/* 导航按钮 */}
        <div className="flex justify-between mb-8">
          <button
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handlePrevQuestion}
            disabled={currentQuestion === 0}
          >
            上一题
          </button>
          <button
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleNextQuestion}
            disabled={currentQuestion === questions.length - 1}
          >
            下一题
          </button>
        </div>

        {/* 提交按钮 */}
        <button
          className="w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={handleSubmit}
          disabled={progress < 100}
        >
          提交并查看结果
        </button>

        {/* 返回首页按钮 */}
        <button
          className="w-full mt-4 py-2 bg-white text-purple-600 border border-purple-600 rounded-lg hover:bg-purple-50 transition-all"
          onClick={() => navigate("/")}
        >
          返回首页
        </button>
      </div>
    </div>
  );
};

export default Test;