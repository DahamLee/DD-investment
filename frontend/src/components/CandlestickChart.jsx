import { useEffect, useRef, useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'
import 'chartjs-adapter-date-fns'

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
)

export default function CandlestickChart({ candles, indicators = [] }) {
  const chartRef = useRef()
  const [chartData, setChartData] = useState(null)

  useEffect(() => {
    if (candles && candles.length > 0) {
      prepareChartData()
    }
  }, [candles, indicators])

  function prepareChartData() {
    // 캔들 데이터를 Chart.js 형식으로 변환
    const labels = candles.map(candle => candle.date)
    
    // OHLC 데이터를 바 차트용으로 변환
    const datasets = [
      {
        label: '시가',
        data: candles.map(candle => candle.open),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
        type: 'bar'
      },
      {
        label: '고가',
        data: candles.map(candle => candle.high),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
        type: 'bar'
      },
      {
        label: '저가',
        data: candles.map(candle => candle.low),
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
        type: 'bar'
      },
      {
        label: '종가',
        data: candles.map(candle => candle.close),
        backgroundColor: 'rgba(255, 206, 86, 0.6)',
        borderColor: 'rgba(255, 206, 86, 1)',
        borderWidth: 2,
        type: 'line',
        tension: 0.1
      }
    ]

    // 기술지표 추가
    if (indicators && indicators.length > 0) {
      // 이동평균선 추가
      if (indicators.some(ind => ind.ma5 !== null)) {
        datasets.push({
          label: 'MA5',
          data: indicators.map(ind => ind.ma5),
          backgroundColor: 'rgba(153, 102, 255, 0.3)',
          borderColor: 'rgba(153, 102, 255, 1)',
          borderWidth: 1,
          type: 'line',
          tension: 0.1,
          pointRadius: 0
        })
      }

      if (indicators.some(ind => ind.ma20 !== null)) {
        datasets.push({
          label: 'MA20',
          data: indicators.map(ind => ind.ma20),
          backgroundColor: 'rgba(255, 159, 64, 0.3)',
          borderColor: 'rgba(255, 159, 64, 1)',
          borderWidth: 1,
          type: 'line',
          tension: 0.1,
          pointRadius: 0
        })
      }

      if (indicators.some(ind => ind.ma60 !== null)) {
        datasets.push({
          label: 'MA60',
          data: indicators.map(ind => ind.ma60),
          backgroundColor: 'rgba(201, 203, 207, 0.3)',
          borderColor: 'rgba(201, 203, 207, 1)',
          borderWidth: 1,
          type: 'line',
          tension: 0.1,
          pointRadius: 0
        })
      }
    }

    setChartData({
      labels,
      datasets
    })
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: '주식 캔들차트'
      },
      legend: {
        display: true,
        position: 'top'
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: function(context) {
            const label = context.dataset.label || ''
            const value = context.parsed.y
            return `${label}: ${value.toLocaleString()}원`
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: '날짜'
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: '가격 (원)'
        },
        ticks: {
          callback: function(value) {
            return value.toLocaleString()
          }
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    }
  }

  if (!chartData) {
    return (
      <div style={{ 
        height: 400, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        border: '1px solid #eee',
        borderRadius: 8,
        background: '#f9f9f9'
      }}>
        <div>차트 데이터를 로딩 중...</div>
      </div>
    )
  }

  return (
    <div style={{ height: 400, width: '100%' }}>
      <Bar ref={chartRef} data={chartData} options={options} />
    </div>
  )
}
