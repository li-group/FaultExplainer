# # import pandas as pd
# # import numpy as np
# # from sklearn.decomposition import PCA
# # from sklearn.preprocessing import StandardScaler
# # import uuid


# # class FaultDetectionModel:
# #     def __init__(self, n_components=0.9, alpha=0.05):
# #         self.scaler = StandardScaler()
# #         self.pca = PCA(n_components=n_components)
# #         self.data_buffer = pd.DataFrame()
# #         self.fault_callbacks = []
# #         self.alpha = alpha
# #         self.t2_threshold = None
# #         self.current_fault_id = None
# #         self.post_fault_data_count = 0
# #         self.post_fault_threshold = (
# #             20  # Number of data points to collect after initial fault detection
# #         )

# #     def fit(self, training_df):
# #         self.feature_names = training_df.columns.to_list()
# #         Z = self.scaler.fit_transform(training_df)
# #         self.pca.fit(Z)
# #         self.a = self.pca.n_components_
# #         self.m = self.pca.n_features_in_
# #         self.n = self.pca.n_samples_
# #         self.P = self.pca.components_.T
# #         self.lamda = self.pca.explained_variance_
# #         # set thresholds
# #         self.set_t2_threshold()

# #     def set_t2_threshold(self):
# #         assert hasattr(self.pca, "n_samples_"), "Model hasn't been trained"
# #         from scipy.stats import f

# #         scaling_factor = (self.a * (self.n - 1) * (self.n + 1)) / (
# #             self.n * (self.n - self.a)
# #         )
# #         self.t2_threshold = scaling_factor * f.ppf(
# #             1 - self.alpha, self.a, self.n - self.a
# #         )

# #     def register_fault_callback(self, callback):
# #         assert callable(callback)
# #         self.fault_callbacks.append(callback)

# #     def calculate_t2_stat(self, data_point):
# #         # Calculate T^2 statistic
# #         assert isinstance(data_point, pd.DataFrame)
# #         x = data_point[self.feature_names]
# #         z = self.scaler.transform(x)
# #         t2_stat = z @ self.P @ np.diag(self.lamda**-1) @ self.P.T @ z.T
# #         return t2_stat.item()

# #     def is_anomaly(self, data_point):
# #         t2_stat = self.calculate_t2_stat(data_point)
# #         anomaly = t2_stat > self.t2_threshold
# #         return anomaly, t2_stat

# #     def process_data_point(self, data_point):
# #         anomaly, t2_stat = self.is_anomaly(data_point)
# #         data_point[["T^2_stat", "Anomaly"]] = [t2_stat, anomaly]
# #         self.data_buffer = pd.concat([self.data_buffer, data_point], ignore_index=True)

# #         # if anomaly:
# #         #     for callback in self.fault_callbacks:
# #         #         callback(data_point, t2_stat)
# #         # return anomaly

# #         if anomaly:
# #             if self.current_fault_id is None:
# #                 self.current_fault_id = uuid.uuid4()  # Assign a new fault ID
# #                 self.post_fault_data_count = 0
# #             else:
# #                 self.post_fault_data_count += 1
# #                 if self.post_fault_data_count == self.post_fault_threshold:
# #                     # Trigger fault handling after collecting enough data points
# #                     for callback in self.fault_callbacks:
# #                         callback(
# #                             {"data": data_point, "fault_id": self.current_fault_id}
# #                         )
# #         else:
# #             if self.current_fault_id is not None:
# #                 # Fault has ended
# #                 self.current_fault_id = None
# #                 self.post_fault_data_count = 0

# #         return t2_stat, anomaly

# #     def plot(self):
# #         import plotly.express as px

# #         fig = px.line(self.data_buffer, y="T^2_stat", title="T^2 Statistics Over Time")
# #         fig.add_hline(y=self.t2_threshold)

# #         in_fault = False
# #         for i, t2_stat in enumerate(self.data_buffer["T^2_stat"]):
# #             if t2_stat > self.t2_threshold and not in_fault:
# #                 start_fault = i
# #                 in_fault = True
# #             elif t2_stat <= self.t2_threshold and in_fault:
# #                 end_fault = i
# #                 # Add a red shape for the fault period
# #                 fig.add_shape(
# #                     type="rect",
# #                     x0=start_fault,
# #                     y0=0,
# #                     x1=end_fault,
# #                     y1=1,
# #                     line=dict(width=0),
# #                     fillcolor="red",
# #                     opacity=0.2,
# #                     layer="below",
# #                     xref="x",
# #                     yref="paper",
# #                 )
# #                 in_fault = False

# #         # Check if the last data point is still in a fault period
# #         if in_fault:
# #             fig.add_shape(
# #                 type="rect",
# #                 x0=start_fault,
# #                 y0=0,
# #                 x1=len(self.data_buffer),
# #                 y1=1,
# #                 line=dict(width=0),
# #                 fillcolor="red",
# #                 opacity=0.2,
# #                 layer="below",
# #                 xref="x",
# #                 yref="paper",
# #             )

# #         fig.update_layout(xaxis_title="Time", yaxis_title="T^2 Statistic")
# #         return fig

# #     def t2_contrib(self, timestamp):
# #         x = self.data_buffer[self.data_buffer["timestamp"] == timestamp][
# #             self.feature_names
# #         ]
# #         z = self.scaler.transform(x)[0]
# #         # Precompute t as a vector
# #         t = z.T @ self.P

# #         # Vectorized calculation of c(j, i)
# #         def calculate_c(j):
# #             c_ji = (t  g self.lamda) * self.P[j, :] * (z[j])  # - self.scaler.mean_[j])
# #             return np.maximum(c_ji, 0)  # Ensures non-negativity

# #         # Calculate C(j) for each j
# #         C_list = np.array([calculate_c(j).sum() for j in range(len(z))])

# #         return C_list

# #     def plot_t2_contributions(self, start_index, end_index=None):
# #         import plotly.express as px

# #         if end_index == None:
# #             end_index = start_index
# #         contributions = []
# #         for index in range(start_index, end_index + 1):
# #             # x_j = self.data_buffer.iloc[index].values
# #             contrib = self.t2_contrib(index)
# #             contributions.append(contrib)

# #         # Create DataFrame for animation
# #         timestamps = self.data_buffer["timestamp"][start_index : end_index + 1]
# #         # feature_names = [f'Feature {i+1}' for i in range(P.shape[1])]
# #         feature_names = self.feature_names

# #         animation_df = pd.DataFrame(
# #             contributions, columns=feature_names, index=timestamps
# #         ).reset_index()
# #         animation_df = animation_df.melt(
# #             id_vars="timestamp", var_name="Feature", value_name="T2 Contribution"
# #         )

# #         # Create Animated Bar Plot
# #         fig = px.bar(
# #             animation_df,
# #             x="Feature",
# #             y="T2 Contribution",
# #             animation_frame="timestamp",
# #             range_y=[0, animation_df["T2 Contribution"].max()],
# #         )

# #         fig.update_layout(title_text="T^2 Contributions Over Time")
# #         return fig


# import pandas as pd
# import numpy as np
# from sklearn.decomposition import PCA
# from sklearn.preprocessing import StandardScaler
# import uuid


# class FaultDetectionModel:
#     def __init__(self, n_components=0.9, alpha=0.05):
#         self.scaler = StandardScaler()
#         self.pca = PCA(n_components=n_components)
#         self.data_buffer = pd.DataFrame()
#         self.fault_callbacks = []
#         self.alpha = alpha
#         self.t2_threshold = None
#         self.current_fault_id = None
#         self.post_fault_data_count = 0
#         self.post_fault_threshold = (
#             20  # Number of data points to collect after initial fault detection
#         )

#     def fit(self, training_df):
#         self.feature_names = training_df.columns.to_list()
#         Z = self.scaler.fit_transform(training_df)
#         self.pca.fit(Z)
#         self.a = self.pca.n_components_
#         self.m = self.pca.n_features_in_
#         self.n = self.pca.n_samples_
#         self.P = self.pca.components_.T
#         self.lamda = self.pca.explained_variance_
#         # set thresholds
#         self.set_t2_threshold()

#     def set_t2_threshold(self):
#         assert hasattr(self.pca, "n_samples_"), "Model hasn't been trained"
#         from scipy.stats import f

#         scaling_factor = (self.a * (self.n - 1) * (self.n + 1)) / (
#             self.n * (self.n - self.a)
#         )
#         self.t2_threshold = scaling_factor * f.ppf(
#             1 - self.alpha, self.a, self.n - self.a
#         )

#     def register_fault_callback(self, callback):
#         assert callable(callback)
#         self.fault_callbacks.append(callback)

#     def calculate_t2_stat(self, data_point):
#         # Calculate T^2 statistic
#         assert isinstance(data_point, pd.DataFrame)
#         x = data_point[self.feature_names]
#         z = self.scaler.transform(x)
#         t2_stat = z @ self.P @ np.diag(self.lamda**-1) @ self.P.T @ z.T
#         return t2_stat.item()

#     def is_anomaly(self, data_point):
#         t2_stat = self.calculate_t2_stat(data_point)
#         anomaly = t2_stat > self.t2_threshold
#         return anomaly, t2_stat

#     def process_data_point(self, data_point):
#         anomaly, t2_stat = self.is_anomaly(data_point)
#         data_point[["T^2_stat", "Anomaly"]] = [t2_stat, anomaly]
#         self.data_buffer = pd.concat([self.data_buffer, data_point], ignore_index=True)

#         # if anomaly:
#         #     for callback in self.fault_callbacks:
#         #         callback(data_point, t2_stat)
#         # return anomaly

#         if anomaly:
#             if self.current_fault_id is None:
#                 self.current_fault_id = uuid.uuid4()  # Assign a new fault ID
#                 self.post_fault_data_count = 0
#             else:
#                 self.post_fault_data_count += 1
#                 if self.post_fault_data_count == self.post_fault_threshold:
#                     # Trigger fault handling after collecting enough data points
#                     for callback in self.fault_callbacks:
#                         callback(
#                             {"data": data_point, "fault_id": self.current_fault_id}
#                         )
#         else:
#             if self.current_fault_id is not None:
#                 # Fault has ended
#                 self.current_fault_id = None
#                 self.post_fault_data_count = 0

#         return t2_stat, anomaly

#     def plot(self):
#         import plotly.express as px

#         fig = px.line(self.data_buffer, y="T^2_stat", title="T^2 Statistics Over Time")
#         fig.add_hline(y=self.t2_threshold)

#         in_fault = False
#         for i, t2_stat in enumerate(self.data_buffer["T^2_stat"]):
#             if t2_stat > self.t2_threshold and not in_fault:
#                 start_fault = i
#                 in_fault = True
#             elif t2_stat <= self.t2_threshold and in_fault:
#                 end_fault = i
#                 # Add a red shape for the fault period
#                 fig.add_shape(
#                     type="rect",
#                     x0=start_fault,
#                     y0=0,
#                     x1=end_fault,
#                     y1=1,
#                     line=dict(width=0),
#                     fillcolor="red",
#                     opacity=0.2,
#                     layer="below",
#                     xref="x",
#                     yref="paper",
#                 )
#                 in_fault = False

#         # Check if the last data point is still in a fault period
#         if in_fault:
#             fig.add_shape(
#                 type="rect",
#                 x0=start_fault,
#                 y0=0,
#                 x1=len(self.data_buffer),
#                 y1=1,
#                 line=dict(width=0),
#                 fillcolor="red",
#                 opacity=0.2,
#                 layer="below",
#                 xref="x",
#                 yref="paper",
#             )

#         fig.update_layout(xaxis_title="Time", yaxis_title="T^2 Statistic")
#         return fig

#     def t2_contrib(self, timestamp):
#         x = self.data_buffer[self.data_buffer["timestamp"] == timestamp][
#             self.feature_names
#         ]
#         z = self.scaler.transform(x)[0]
#         # Precompute t as a vector
#         t = z.T @ self.P

#         # Vectorized calculation of c(j, i)
#         def calculate_c(j):
#             c_ji = (t / self.lamda) * self.P[j, :] * (z[j])  # - self.scaler.mean_[j])
#             return np.maximum(c_ji, 0)  # Ensures non-negativity

#         # Calculate C(j) for each j
#         C_list = np.array([calculate_c(j).sum() for j in range(len(z))])

#         return C_list

#     def plot_t2_contributions(self, start_index, end_index=None):
#         import plotly.express as px

#         if end_index == None:
#             end_index = start_index
#         contributions = []
#         for index in range(start_index, end_index + 1):
#             # x_j = self.data_buffer.iloc[index].values
#             contrib = self.t2_contrib(index)
#             contributions.append(contrib)

#         # Create DataFrame for animation
#         timestamps = self.data_buffer["timestamp"][start_index : end_index + 1]
#         # feature_names = [f'Feature {i+1}' for i in range(P.shape[1])]
#         feature_names = self.feature_names

#         animation_df = pd.DataFrame(
#             contributions, columns=feature_names, index=timestamps
#         ).reset_index()
#         animation_df = animation_df.melt(
#             id_vars="timestamp", var_name="Feature", value_name="T2 Contribution"
#         )

#         # Create Animated Bar Plot
#         fig = px.bar(
#             animation_df,
#             x="Feature",
#             y="T2 Contribution",
#             animation_frame="timestamp",
#             range_y=[0, animation_df["T2 Contribution"].max()],
#         )

#         fig.update_layout(title_text="T^2 Contributions Over Time")
#         return fig


# import pandas as pd
# import numpy as np
# from sklearn.decomposition import PCA
# from sklearn.preprocessing import StandardScaler
# import uuid


# class FaultDetectionModel:
#     def __init__(self, n_components=0.9, alpha=0.05):
#         self.scaler = StandardScaler()
#         self.pca = PCA(n_components=n_components)
#         self.data_buffer = pd.DataFrame()
#         self.fault_callbacks = []
#         self.alpha = alpha
#         self.t2_threshold = None
#         self.current_fault_id = None
#         self.post_fault_data_count = 0
#         self.post_fault_threshold = (
#             20  # Number of data points to collect after initial fault detection
#         )

#     def fit(self, training_df):
#         self.feature_names = training_df.columns.to_list()
#         Z = self.scaler.fit_transform(training_df)
#         self.pca.fit(Z)
#         self.a = self.pca.n_components_
#         self.m = self.pca.n_features_in_
#         self.n = self.pca.n_samples_
#         self.P = self.pca.components_.T
#         self.lamda = self.pca.explained_variance_
#         # set thresholds
#         self.set_t2_threshold()

#     def set_t2_threshold(self):
#         assert hasattr(self.pca, "n_samples_"), "Model hasn't been trained"
#         from scipy.stats import f

#         scaling_factor = (self.a * (self.n - 1) * (self.n + 1)) / (
#             self.n * (self.n - self.a)
#         )
#         self.t2_threshold = scaling_factor * f.ppf(
#             1 - self.alpha, self.a, self.n - self.a
#         )

#     def register_fault_callback(self, callback):
#         assert callable(callback)
#         self.fault_callbacks.append(callback)

#     def calculate_t2_stat(self, data_point):
#         # Calculate T^2 statistic
#         assert isinstance(data_point, pd.DataFrame)
#         x = data_point[self.feature_names]
#         z = self.scaler.transform(x)
#         t2_stat = z @ self.P @ np.diag(self.lamda**-1) @ self.P.T @ z.T
#         return t2_stat.item()

#     def is_anomaly(self, data_point):
#         t2_stat = self.calculate_t2_stat(data_point)
#         anomaly = t2_stat > self.t2_threshold
#         return anomaly, t2_stat

#     def process_data_point(self, data_point):
#         anomaly, t2_stat = self.is_anomaly(data_point)
#         data_point[["T^2_stat", "Anomaly"]] = [t2_stat, anomaly]
#         self.data_buffer = pd.concat([self.data_buffer, data_point], ignore_index=True)

#         # if anomaly:
#         #     for callback in self.fault_callbacks:
#         #         callback(data_point, t2_stat)
#         # return anomaly

#         if anomaly:
#             if self.current_fault_id is None:
#                 self.current_fault_id = uuid.uuid4()  # Assign a new fault ID
#                 self.post_fault_data_count = 0
#             else:
#                 self.post_fault_data_count += 1
#                 if self.post_fault_data_count == self.post_fault_threshold:
#                     # Trigger fault handling after collecting enough data points
#                     for callback in self.fault_callbacks:
#                         callback(
#                             {"data": data_point, "fault_id": self.current_fault_id}
#                         )
#         else:
#             if self.current_fault_id is not None:
#                 # Fault has ended
#                 self.current_fault_id = None
#                 self.post_fault_data_count = 0

#         return t2_stat, anomaly

#     def plot(self):
#         import plotly.express as px

#         fig = px.line(self.data_buffer, y="T^2_stat", title="T^2 Statistics Over Time")
#         fig.add_hline(y=self.t2_threshold)

#         in_fault = False
#         for i, t2_stat in enumerate(self.data_buffer["T^2_stat"]):
#             if t2_stat > self.t2_threshold and not in_fault:
#                 start_fault = i
#                 in_fault = True
#             elif t2_stat <= self.t2_threshold and in_fault:
#                 end_fault = i
#                 # Add a red shape for the fault period
#                 fig.add_shape(
#                     type="rect",
#                     x0=start_fault,
#                     y0=0,
#                     x1=end_fault,
#                     y1=1,
#                     line=dict(width=0),
#                     fillcolor="red",
#                     opacity=0.2,
#                     layer="below",
#                     xref="x",
#                     yref="paper",
#                 )
#                 in_fault = False

#         # Check if the last data point is still in a fault period
#         if in_fault:
#             fig.add_shape(
#                 type="rect",
#                 x0=start_fault,
#                 y0=0,
#                 x1=len(self.data_buffer),
#                 y1=1,
#                 line=dict(width=0),
#                 fillcolor="red",
#                 opacity=0.2,
#                 layer="below",
#                 xref="x",
#                 yref="paper",
#             )

#         fig.update_layout(xaxis_title="Time", yaxis_title="T^2 Statistic")
#         return fig

#     def t2_contrib(self, timestamp):
#         x = self.data_buffer[self.data_buffer["timestamp"] == timestamp][
#             self.feature_names
#         ]
#         z = self.scaler.transform(x)[0]
#         # Precompute t as a vector
#         t = z.T @ self.P

#         # Vectorized calculation of c(j, i)
#         def calculate_c(j):
#             c_ji = (t  g self.lamda) * self.P[j, :] * (z[j])  # - self.scaler.mean_[j])
#             return np.maximum(c_ji, 0)  # Ensures non-negativity

#         # Calculate C(j) for each j
#         C_list = np.array([calculate_c(j).sum() for j in range(len(z))])

#         return C_list

#     def plot_t2_contributions(self, start_index, end_index=None):
#         import plotly.express as px

#         if end_index == None:
#             end_index = start_index
#         contributions = []
#         for index in range(start_index, end_index + 1):
#             # x_j = self.data_buffer.iloc[index].values
#             contrib = self.t2_contrib(index)
#             contributions.append(contrib)

#         # Create DataFrame for animation
#         timestamps = self.data_buffer["timestamp"][start_index : end_index + 1]
#         # feature_names = [f'Feature {i+1}' for i in range(P.shape[1])]
#         feature_names = self.feature_names

#         animation_df = pd.DataFrame(
#             contributions, columns=feature_names, index=timestamps
#         ).reset_index()
#         animation_df = animation_df.melt(
#             id_vars="timestamp", var_name="Feature", value_name="T2 Contribution"
#         )

#         # Create Animated Bar Plot
#         fig = px.bar(
#             animation_df,
#             x="Feature",
#             y="T2 Contribution",
#             animation_frame="timestamp",
#             range_y=[0, animation_df["T2 Contribution"].max()],
#         )

#         fig.update_layout(title_text="T^2 Contributions Over Time")
#         return fig


import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import uuid


class FaultDetectionModel:
    def __init__(self, n_components=0.9, alpha=0.05):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components)
        self.data_buffer = pd.DataFrame()
        self.fault_callbacks = []
        self.alpha = alpha
        self.t2_threshold = None
        self.current_fault_id = None
        self.post_fault_data_count = 0
        self.post_fault_threshold = (
            20  # Number of data points to collect after initial fault detection
        )

    def fit(self, training_df):
        self.feature_names = training_df.columns.to_list()
        Z = self.scaler.fit_transform(training_df)
        self.pca.fit(Z)
        self.a = self.pca.n_components_
        self.m = self.pca.n_features_in_
        self.n = self.pca.n_samples_
        self.P = self.pca.components_.T
        self.lamda = self.pca.explained_variance_
        # set thresholds
        self.set_t2_threshold()

    def set_t2_threshold(self):
        assert hasattr(self.pca, "n_samples_"), "Model hasn't been trained"
        from scipy.stats import f

        scaling_factor = (self.a * (self.n - 1) * (self.n + 1)) / (
            self.n * (self.n - self.a)
        )
        self.t2_threshold = scaling_factor * f.ppf(
            1 - self.alpha, self.a, self.n - self.a
        )

    def register_fault_callback(self, callback):
        assert callable(callback)
        self.fault_callbacks.append(callback)

    def calculate_t2_stat(self, data_point):
        # Calculate T^2 statistic
        assert isinstance(data_point, pd.DataFrame)
        x = data_point[self.feature_names]
        z = self.scaler.transform(x)
        t2_stat = z @ self.P @ np.diag(self.lamda**-1) @ self.P.T @ z.T
        return t2_stat.item()

    def is_anomaly(self, data_point):
        t2_stat = self.calculate_t2_stat(data_point)
        anomaly = t2_stat > self.t2_threshold
        return anomaly, t2_stat

    def process_data_point(self, data_point):
        anomaly, t2_stat = self.is_anomaly(data_point)
        data_point[["T^2_stat", "Anomaly"]] = [t2_stat, anomaly]
        self.data_buffer = pd.concat([self.data_buffer, data_point], ignore_index=True)

        # if anomaly:
        #     for callback in self.fault_callbacks:
        #         callback(data_point, t2_stat)
        # return anomaly

        if anomaly:
            if self.current_fault_id is None:
                self.current_fault_id = uuid.uuid4()  # Assign a new fault ID
                self.post_fault_data_count = 0
            else:
                self.post_fault_data_count += 1
                if self.post_fault_data_count == self.post_fault_threshold:
                    # Trigger fault handling after collecting enough data points
                    for callback in self.fault_callbacks:
                        callback(
                            {"data": data_point, "fault_id": self.current_fault_id}
                        )
        else:
            if self.current_fault_id is not None:
                # Fault has ended
                self.current_fault_id = None
                self.post_fault_data_count = 0

        return t2_stat, anomaly

    def plot(self):
        import plotly.express as px

        fig = px.line(self.data_buffer, y="T^2_stat", title="T^2 Statistics Over Time")
        fig.add_hline(y=self.t2_threshold)

        in_fault = False
        for i, t2_stat in enumerate(self.data_buffer["T^2_stat"]):
            if t2_stat > self.t2_threshold and not in_fault:
                start_fault = i
                in_fault = True
            elif t2_stat <= self.t2_threshold and in_fault:
                end_fault = i
                # Add a red shape for the fault period
                fig.add_shape(
                    type="rect",
                    x0=start_fault,
                    y0=0,
                    x1=end_fault,
                    y1=1,
                    line=dict(width=0),
                    fillcolor="red",
                    opacity=0.2,
                    layer="below",
                    xref="x",
                    yref="paper",
                )
                in_fault = False

        # Check if the last data point is still in a fault period
        if in_fault:
            fig.add_shape(
                type="rect",
                x0=start_fault,
                y0=0,
                x1=len(self.data_buffer),
                y1=1,
                line=dict(width=0),
                fillcolor="red",
                opacity=0.2,
                layer="below",
                xref="x",
                yref="paper",
            )

        fig.update_layout(xaxis_title="Time", yaxis_title="T^2 Statistic")
        return fig

    def t2_contrib(self, timestamp):
        x = self.data_buffer[self.data_buffer["timestamp"] == timestamp][
            self.feature_names
        ]
        z = self.scaler.transform(x)[0]
        # Precompute t as a vector
        t = z.T @ self.P

        # Vectorized calculation of c(j, i)
        def calculate_c(j):
            c_ji = (t / self.lamda) * self.P[j, :] * (z[j])  # - self.scaler.mean_[j])
            return np.maximum(c_ji, 0)  # Ensures non-negativity

        # Calculate C(j) for each j
        C_list = np.array([calculate_c(j).sum() for j in range(len(z))])

        return C_list

    def plot_t2_contributions(self, start_index, end_index=None):
        import plotly.express as px

        if end_index == None:
            end_index = start_index
        contributions = []
        for index in range(start_index, end_index + 1):
            # x_j = self.data_buffer.iloc[index].values
            contrib = self.t2_contrib(index)
            contributions.append(contrib)

        # Create DataFrame for animation
        timestamps = self.data_buffer["timestamp"][start_index : end_index + 1]
        # feature_names = [f'Feature {i+1}' for i in range(P.shape[1])]
        feature_names = self.feature_names

        animation_df = pd.DataFrame(
            contributions, columns=feature_names, index=timestamps
        ).reset_index()
        animation_df = animation_df.melt(
            id_vars="timestamp", var_name="Feature", value_name="T2 Contribution"
        )

        # Create Animated Bar Plot
        fig = px.bar(
            animation_df,
            x="Feature",
            y="T2 Contribution",
            animation_frame="timestamp",
            range_y=[0, animation_df["T2 Contribution"].max()],
        )

        fig.update_layout(title_text="T^2 Contributions Over Time")
        return fig
