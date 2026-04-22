import React, { useState } from 'react';
import { X, Server, User, Lock, Globe, Loader2 } from 'lucide-react';
import { api } from '../api';
import { useAppContext } from '../context/AppContext';

const AddPCModal = () => {
    const { isAddPCModalOpen, setIsAddPCModalOpen } = useAppContext();
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        hostname: '',
        ip: '',
        user: '',
        password: ''
    });

    if (!isAddPCModalOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const response = await api.addNode(formData);
            if (response.status === 'success') {
                alert('PC Added Successfully! Please refresh the dashboard.');
                setIsAddPCModalOpen(false);
                setFormData({ hostname: '', ip: '', user: '', password: '' });
                window.location.reload(); // Refresh to see the new node
            } else {
                alert('Error: ' + response.message);
            }
        } catch (error) {
            console.error(error);
            alert('Failed to connect to backend server.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    return (
        <div className="modal-overlay" onClick={() => setIsAddPCModalOpen(false)}>
            <div className="modal-container" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <div className="modal-title">
                        <Server className="modal-icon" />
                        <h3>Register New PC</h3>
                    </div>
                    <button className="close-btn" onClick={() => setIsAddPCModalOpen(false)}>
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="form-group">
                        <label><Server size={14} /> Hostname</label>
                        <input
                            type="text"
                            name="hostname"
                            placeholder="e.g. CSE-ICB-057"
                            required
                            value={formData.hostname}
                            onChange={handleChange}
                        />
                        <small>The name of the computer on the network</small>
                    </div>

                    <div className="form-group">
                        <label><Globe size={14} /> IP Address (Optional)</label>
                        <input
                            type="text"
                            name="ip"
                            placeholder="e.g. 172.111.0.146"
                            value={formData.ip}
                            onChange={handleChange}
                        />
                        <small>Provide if hostname resolution is unreliable</small>
                    </div>

                    <div className="grid-2">
                        <div className="form-group">
                            <label><User size={14} /> Username</label>
                            <input
                                type="text"
                                name="user"
                                placeholder="ubuntu"
                                required
                                value={formData.user}
                                onChange={handleChange}
                            />
                        </div>
                        <div className="form-group">
                            <label><Lock size={14} /> Become Password</label>
                            <input
                                type="password"
                                name="password"
                                placeholder="••••••••"
                                required
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    <div className="modal-footer">
                        <button type="button" className="btn btn-secondary" onClick={() => setIsAddPCModalOpen(false)}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn-primary" disabled={isLoading}>
                            {isLoading ? <Loader2 className="animate-spin" size={18} /> : 'Register PC'}
                        </button>
                    </div>
                </form>
            </div>

            <style jsx>{`
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.7);
                    backdrop-filter: blur(8px);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                }
                .modal-container {
                    background: #1e293b;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 1rem;
                    width: 100%;
                    max-width: 500px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                    animation: modalIn 0.3s ease-out;
                }
                @keyframes modalIn {
                    from { opacity: 0; transform: scale(0.95) translateY(10px); }
                    to { opacity: 1; transform: scale(1) translateY(0); }
                }
                .modal-header {
                    padding: 1.5rem;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .modal-title {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }
                .modal-icon {
                    color: #3b82f6;
                }
                .modal-title h3 {
                    margin: 0;
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: #f8fafc;
                }
                .close-btn {
                    background: transparent;
                    border: none;
                    color: #94a3b8;
                    cursor: pointer;
                    transition: color 0.2s;
                }
                .close-btn:hover {
                    color: #f8fafc;
                }
                .modal-form {
                    padding: 1.5rem;
                }
                .form-group {
                    margin-bottom: 1.25rem;
                }
                .form-group label {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    font-size: 0.875rem;
                    font-weight: 500;
                    color: #94a3b8;
                    margin-bottom: 0.5rem;
                }
                .form-group input {
                    width: 100%;
                    background: #0f172a;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 0.5rem;
                    padding: 0.75rem;
                    color: #f8fafc;
                    font-size: 0.9375rem;
                    transition: border-color 0.2s, box-shadow 0.2s;
                }
                .form-group input:focus {
                    outline: none;
                    border-color: #3b82f6;
                    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
                }
                .form-group small {
                    display: block;
                    margin-top: 0.25rem;
                    font-size: 0.75rem;
                    color: #64748b;
                }
                .grid-2 {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1rem;
                }
                .modal-footer {
                    margin-top: 1.5rem;
                    display: flex;
                    justify-content: flex-end;
                    gap: 0.75rem;
                }
                .animate-spin {
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

export default AddPCModal;
