import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Upload, Users, TrendingUp, PieChart } from 'lucide-react';

const SingaporePopulationApp = () => {
  const [csvData, setCsvData] = useState(null);
  const [activeTab, setActiveTab] = useState('total');
  const [loading, setLoading] = useState(false);

  // Sample data structure - in real Streamlit, this would come from uploaded CSV
  const sampleData = [
    { Year: 2000, Residents: "Total Residents", Count: 3273363 },
    { Year: 2000, Residents: "Total Male Residents", Count: 1634667 },
    { Year: 2000, Residents: "Total Female Residents", Count: 1638696 },
    // Add more sample rows as needed
  ];

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const text = e.target.result;
      const rows = text.split('\n').map(row => row.split(','));
      const headers = rows[0];
      const data = rows.slice(1).filter(row => row.length === headers.length).map(row => ({
        Year: parseInt(row[0]),
        Residents: row[1],
        Count: parseInt(row[2])
      }));
      setCsvData(data);
      setLoading(false);
    };
    
    reader.readAsText(file);
  };

  // Calculate total population by year
  const getTotalPopulation = () => {
    if (!csvData) return [];
    
    const grouped = {};
    csvData.forEach(row => {
      if (!grouped[row.Year]) grouped[row.Year] = 0;
      grouped[row.Year] += row.Count;
    });
    
    return Object.entries(grouped).map(([year, total]) => ({
      year: parseInt(year),
      total
    })).sort((a, b) => a.year - b.year);
  };

  // Calculate gender ratios
  const getGenderRatios = () => {
    if (!csvData) return [];
    
    const years = [2000, 2003, 2006, 2009, 2012, 2015, 2018];
    const groups = {
      'Total': ['Total Male Residents', 'Total Female Residents'],
      'Malays': ['Total Male Malays', 'Total Female Malays'],
      'Chinese': ['Total Male Chinese', 'Total Female Chinese'],
      'Indians': ['Total Male Indians', 'Total Female Indians'],
      'Others': ['Other Ethnic Groups (Males)', 'Other Ethnic Groups (Females)']
    };
    
    const ratios = [];
    years.forEach(year => {
      const yearData = { year };
      Object.entries(groups).forEach(([groupName, [maleLabel, femaleLabel]]) => {
        const maleRow = csvData.find(r => r.Year === year && r.Residents === maleLabel);
        const femaleRow = csvData.find(r => r.Year === year && r.Residents === femaleLabel);
        
        if (maleRow && femaleRow) {
          yearData[groupName] = (femaleRow.Count / maleRow.Count).toFixed(4);
        }
      });
      ratios.push(yearData);
    });
    
    return ratios;
  };

  // Calculate population growth
  const getPopulationGrowth = () => {
    if (!csvData) return [];
    
    const totalResidents = csvData
      .filter(r => r.Residents === 'Total Residents')
      .sort((a, b) => a.Year - b.Year);
    
    const basePopulation = totalResidents[0]?.Count || 1;
    
    return totalResidents.map((row, index) => {
      const prevCount = index > 0 ? totalResidents[index - 1].Count : row.Count;
      const yoyGrowth = ((row.Count - prevCount) / prevCount * 100).toFixed(2);
      const totalGrowth = ((row.Count - basePopulation) / basePopulation * 100).toFixed(2);
      
      return {
        year: row.Year,
        population: row.Count,
        yoyGrowth: index === 0 ? 0 : parseFloat(yoyGrowth),
        totalGrowth: parseFloat(totalGrowth)
      };
    });
  };

  const totalPopData = getTotalPopulation();
  const genderRatioData = getGenderRatios();
  const growthData = getPopulationGrowth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h1 className="text-4xl font-bold text-indigo-900 mb-2 flex items-center gap-3">
            <Users className="w-10 h-10" />
            Singapore Population Analysis
          </h1>
          <p className="text-gray-600">Interactive demographic data visualization (2000-2018)</p>
        </div>

        {/* File Upload */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-indigo-300 rounded-lg cursor-pointer hover:bg-indigo-50 transition-colors">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <Upload className="w-10 h-10 text-indigo-500 mb-2" />
              <p className="text-sm text-gray-600">
                <span className="font-semibold">Click to upload</span> Singapore_Residents.csv
              </p>
            </div>
            <input
              type="file"
              className="hidden"
              accept=".csv"
              onChange={handleFileUpload}
            />
          </label>
          {loading && <p className="text-center mt-4 text-indigo-600">Loading data...</p>}
          {csvData && (
            <p className="text-center mt-4 text-green-600 font-semibold">
              ✓ Data loaded successfully ({csvData.length} rows)
            </p>
          )}
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-lg mb-8">
          <div className="flex border-b">
            {[
              { id: 'total', label: 'Total Population', icon: Users },
              { id: 'ratio', label: 'Gender Ratios', icon: PieChart },
              { id: 'growth', label: 'Population Growth', icon: TrendingUp }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-4 font-semibold transition-colors ${
                  activeTab === tab.id
                    ? 'text-indigo-600 border-b-2 border-indigo-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                {tab.label}
              </button>
            ))}
          </div>

          <div className="p-6">
            {!csvData ? (
              <div className="text-center py-12 text-gray-500">
                Please upload a CSV file to see the analysis
              </div>
            ) : (
              <>
                {/* Tab 1: Total Population */}
                {activeTab === 'total' && (
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">
                      Total Population by Year
                    </h2>
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={totalPopData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis />
                        <Tooltip formatter={(value) => value.toLocaleString()} />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="total"
                          stroke="#4f46e5"
                          strokeWidth={3}
                          name="Total Population"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                    
                    <div className="mt-6 overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-indigo-100">
                          <tr>
                            <th className="px-4 py-2 text-left">Year</th>
                            <th className="px-4 py-2 text-right">Total Population</th>
                          </tr>
                        </thead>
                        <tbody>
                          {totalPopData.map((row, idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : ''}>
                              <td className="px-4 py-2">{row.year}</td>
                              <td className="px-4 py-2 text-right font-mono">
                                {row.total.toLocaleString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Tab 2: Gender Ratios */}
                {activeTab === 'ratio' && (
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">
                      Female to Male Ratios (3-Year Intervals)
                    </h2>
                    <ResponsiveContainer width="100%" height={400}>
                      <LineChart data={genderRatioData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis domain={[0.9, 1.2]} />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="Total" stroke="#4f46e5" strokeWidth={2} />
                        <Line type="monotone" dataKey="Malays" stroke="#10b981" strokeWidth={2} />
                        <Line type="monotone" dataKey="Chinese" stroke="#f59e0b" strokeWidth={2} />
                        <Line type="monotone" dataKey="Indians" stroke="#ef4444" strokeWidth={2} />
                        <Line type="monotone" dataKey="Others" stroke="#8b5cf6" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                    
                    <div className="mt-6 overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-indigo-100">
                          <tr>
                            <th className="px-4 py-2 text-left">Year</th>
                            <th className="px-4 py-2 text-center">Total</th>
                            <th className="px-4 py-2 text-center">Malays</th>
                            <th className="px-4 py-2 text-center">Chinese</th>
                            <th className="px-4 py-2 text-center">Indians</th>
                            <th className="px-4 py-2 text-center">Others</th>
                          </tr>
                        </thead>
                        <tbody>
                          {genderRatioData.map((row, idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : ''}>
                              <td className="px-4 py-2 font-semibold">{row.year}</td>
                              <td className="px-4 py-2 text-center font-mono">{row.Total}</td>
                              <td className="px-4 py-2 text-center font-mono">{row.Malays}</td>
                              <td className="px-4 py-2 text-center font-mono">{row.Chinese}</td>
                              <td className="px-4 py-2 text-center font-mono">{row.Indians}</td>
                              <td className="px-4 py-2 text-center font-mono">{row.Others}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Tab 3: Population Growth */}
                {activeTab === 'growth' && (
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">
                      Population Growth Analysis
                    </h2>
                    <ResponsiveContainer width="100%" height={400}>
                      <BarChart data={growthData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis />
                        <Tooltip formatter={(value) => `${value}%`} />
                        <Legend />
                        <Bar dataKey="yoyGrowth" fill="#4f46e5" name="Year-over-Year Growth %" />
                        <Bar dataKey="totalGrowth" fill="#10b981" name="Total Growth from 2000 %" />
                      </BarChart>
                    </ResponsiveContainer>
                    
                    <div className="mt-6 overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-indigo-100">
                          <tr>
                            <th className="px-4 py-2 text-left">Year</th>
                            <th className="px-4 py-2 text-right">Population</th>
                            <th className="px-4 py-2 text-right">YoY Growth %</th>
                            <th className="px-4 py-2 text-right">Total Growth %</th>
                          </tr>
                        </thead>
                        <tbody>
                          {growthData.map((row, idx) => (
                            <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : ''}>
                              <td className="px-4 py-2">{row.year}</td>
                              <td className="px-4 py-2 text-right font-mono">
                                {row.population.toLocaleString()}
                              </td>
                              <td className={`px-4 py-2 text-right font-mono ${
                                row.yoyGrowth > 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {row.yoyGrowth.toFixed(2)}%
                              </td>
                              <td className="px-4 py-2 text-right font-mono text-green-600">
                                {row.totalGrowth.toFixed(2)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-gray-600 text-sm">
          <p>Singapore Residents Population Data (2000-2018)</p>
        </div>
      </div>
    </div>
  );
};

export default SingaporePopulationApp;
